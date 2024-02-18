from pyspark.sql import SparkSession
from .pxlogger import CustomLogger
from .util import parseSourceObject, toTempView
import urllib3
import boto3
from datetime import datetime
import fnmatch

"""
CSV 테이블을 로드하고 저장하는 클래스

:param spark: Spark 세션.
:param default_bucket: Delta 테이블이 저장된 기본 S3 버킷.
:param default_dpath: Delta 테이블의 기본 dpath 또는 하위 디렉토리.
"""

class CSVTableManager:
    def __init__(self, spark, s3_endpoint, s3_access_key, s3_secret_key, s3_ssl_verify, archive_bucket, archive_dpath, bucket, dpath):
        self.spark = spark
        self.default_bucket = bucket
        self.default_dpath = dpath
        self.archive_bucket = archive_bucket
        self.archive_dpath = archive_dpath
        self.logger = CustomLogger("CSVTableManager")
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        self.s3_client = boto3.client('s3', endpoint_url=s3_endpoint, aws_access_key_id=s3_access_key, aws_secret_access_key=s3_secret_key, verify=s3_ssl_verify)
         
    def getType(self) :
        return "csv"
    
    def getTablePath(self, bucket, dpath, tableName):
        if bucket is None:
            bucket = self.default_bucket
        if dpath is None:
            dpath = self.default_dpath
            
        return f's3a://{bucket}/{tableName}' if dpath is None else f's3a://{bucket}/{dpath}/{tableName}'

    
    def loadTable(self, file_name, offset=None, chunk_size=100000, bucket=None, dpath=None, customSchema=None, header=True, infer_schema=True, delemeter=None, charset=None): 
        self.logger.debug(("loadTable = ", file_name, bucket, dpath))
        
        file_path = self.getTablePath(bucket, dpath, file_name)
        self.logger.debug(("file_path = ", file_path))

        if delemeter is None:
           delemeter = "," # r",|\||\t"

        csv_df = None
        try:

            # self.logger.debug((file_name, header, infer_schema, bucket, dpath, customSchema))

            if charset is None:
                charset = "euc-kr"

            if customSchema:
                schema = toCustomSchema(customSchema)
                # 만약 customSchema가 제공되면 해당 스키마를 사용하여 DataFrame을 생성
                csv_df = self.spark.read \
                    .option("header", header) \
                    .option("inferSchema", infer_schema) \
                    .option("delimiter", delemeter) \
                    .option("charset", charset) \
                    .schema(schema) \
                    .csv(file_path)
            else:
                # customSchema가 제공되지 않으면 기본 설정으로 DataFrame 생성
                csv_df = self.spark.read \
                    .option("header", header) \
                    .option("inferSchema", infer_schema) \
                    .option("delimiter", delemeter) \
                    .option("charset", charset) \
                    .csv(file_path)
           
            # TB_HH_PPLTN_INFO_*.csv > TB_HH_PPLTN_INFO 로딩
            table_name = toTempView(file_name)
            csv_df.createOrReplaceTempView(table_name)

            self.logger.debug(("TempView = ", table_name))

        except Exception as e:
            csv_df = None
            self.logger.error(("File not found: ", file_path))
            #self.logger.debug(("File not found: ", str(e)))

        return csv_df


    def loadTables(self, file_names, bucket=None, dpath=None, customSchemas=None, header=True, infer_schema=True, delemeter=None, charset=None):
        file_names = parseSourceObject(file_names)
        dataframes = {}

        # customSchemas가 제공되지 않으면 모든 파일에 대해 None으로 설정
        if customSchemas is None:
            customSchemas = [None] * len(file_names)

        for file_name, customSchema in zip(file_names, customSchemas):
            df = self.loadTable(file_name, bucket=bucket, dpath=dpath, customSchema=customSchema, header=header, infer_schema=infer_schema, charset=charset)
            #table_name = file_name.split('.')[0]  # Assuming the file name without extension is used as the table name
            #df.createOrReplaceTempView(table_name)
            table_name = toTempView(file_name)
            dataframes[table_name] = df

        return dataframes

    def queryTable(self, query, tableNames=None, bucket=None, dpath=None, customSchemas=None, header=True, infer_schema=True, delemeter=None, charset=None):
        self.logger.debug(("queryTable = ", query, tableNames))

        if tableNames is not None:
            self.loadTables(tableNames, bucket=bucket, dpath=dpath, customSchemas=customSchemas, header=header, infer_schema=infer_schema, delemeter=delemeter, charset=charset)

        csv_df = self.spark.sql(query)

        return csv_df

    def archive(self, file_name, bucket=None, dpath=None):
        self.logger.debug(("archive = ", file_name, bucket, dpath))
                
        if bucket is None:
            bucket = self.default_bucket
        if dpath is None:
            dpath = self.default_dpath

        if self.archive_bucket is None: # No Archiving
            return 

        try:
            # S3 버킷 내 파일 목록 가져오기
            objects = self.s3_client.list_objects_v2(Bucket=bucket, Prefix=dpath)
            file_list = [obj['Key'] for obj in objects.get('Contents', [])]
            self.logger.debug(("archive filelists=", file_list))
            # file_name 패턴에 매칭되는 파일 목록 필터링
            matching_files = [file[len(dpath) + 1:] for file in file_list if fnmatch.fnmatchcase(file[len(dpath) + 1:], file_name)]
            self.logger.debug(("archive matching files=", matching_files))
            # 각 파일을 복제하고 삭제
            for filename in matching_files:

                #destination_key = f'{dpath}/archive/{source_key}'  # 변경 필요
                destination_key = self._getArchivePath(filename, dpath)
                source_key = filename if dpath is None else f'{dpath}/{filename}'
                self.copy_and_delete(bucket, source_key, destination_key)

        except Exception as e:
            self.logger.error(("Error moving file to archive:", e))

    def copy_and_delete(self, bucket, source_key, destination_key):
        try:
            # 파일 복제
            self.s3_client.copy_object(
                CopySource={'Bucket': bucket, 'Key': source_key},
                Bucket=self.archive_bucket,
                Key=destination_key
            )

            # 원본 파일 삭제
            self.s3_client.delete_object(Bucket=bucket, Key=source_key)
            self.logger.debug(f'File moved: {bucket}/{source_key} to {self.archive_bucket}/{destination_key}')

        except Exception as e:
            self.logger.error(("Error moving file to archive:", e))

    def _getArchivePath(self, tableName, dpath=None) :
        # 아카이브 경로 초기화
        archive_path = ""

        # dpath가 있으면 추가
        if dpath:
            archive_path += dpath + "/"

        # 현재 날짜 폴더 추가
        current_date = datetime.now().strftime("%Y%m%d")
        archive_path += current_date + "/"

        # tableName 추가
        archive_path += tableName

        return archive_path

    # saveTable(my_dataframe, "output.csv", header=True, mode="overwrite", delimiter=",", charset="UTF-8")
    def saveTable(self, dataFrame, tableName, bucket=None, dpath=None, header=True, mode="append", delimiter=",", charset="euc-kr"):
        self.logger.debug(("saveTable = ", tableName, bucket, dpath, header, mode, delimiter, charset))
        table_path = self.getTablePath(bucket, dpath, tableName)

        dataFrame.write.csv(table_path, header=header, mode=mode, sep=delimiter, encoding=charset)


