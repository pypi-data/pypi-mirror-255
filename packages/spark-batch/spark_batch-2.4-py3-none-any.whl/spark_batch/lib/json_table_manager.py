from pyspark.sql import SparkSession
from .pxlogger import CustomLogger
from .util import parseSourceObject, toTempView
import urllib3
import boto3
from datetime import datetime
import fnmatch

"""
JSON 테이블을 로드하고 저장하는 클래스

:param spark: Spark 세션.
:param default_bucket: Delta 테이블이 저장된 기본 S3 버킷.
:param default_dpath: Delta 테이블의 기본 dpath 또는 하위 디렉토리.
"""

class JSONTableManager:
    def __init__(self, spark, s3_endpoint, s3_access_key, s3_secret_key, s3_ssl_verify, archive_bucket, archive_dpath, bucket, dpath):
        self.spark = spark
        self.default_bucket = bucket
        self.default_dpath = dpath
        self.archive_bucket = archive_bucket
        self.archive_dpath = archive_dpath
        self.logger = CustomLogger("JSONTableManager")
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        self.s3_client = boto3.client('s3', endpoint_url=s3_endpoint, aws_access_key_id=s3_access_key, aws_secret_access_key=s3_secret_key, verify=s3_ssl_verify)
         
    def getType(self) :
        return "json"
    
    def getTablePath(self, bucket, dpath, tableName):
        if bucket is None:
            bucket = self.default_bucket
        if dpath is None:
            dpath = self.default_dpath
            
        return f's3a://{bucket}/{tableName}' if dpath is None else f's3a://{bucket}/{dpath}/{tableName}'
    
    def loadTable(self, file_name, offset=None, chunk_size=100000, bucket=None, dpath=None, customSchema=None, header=True, infer_schema=True): 
        self.logger.debug(("loadTable = ", file_name, bucket, dpath))
        
        file_path = self.getTablePath(bucket, dpath, file_name)
        self.logger.debug(("file_path = ", file_path))

        json_df = None
        try:

            # self.logger.debug((file_name, header, infer_schema, bucket, dpath, customSchema))

            json_df = self.spark.read.json(file_path)

            table_name = toTempView(file_name)
            json_df.createOrReplaceTempView(table_name)

            self.logger.debug(("TempView = ", table_name))

        except Exception as e:
            json_df = None
            #self.logger.debug("File not found: ", str(e))

        return json_df


    def loadTables(self, file_names, bucket=None, dpath=None, customSchemas=None, header=True, infer_schema=True):
        file_names = parseSourceObject(file_names)
        dataframes = {}

        # customSchemas가 제공되지 않으면 모든 파일에 대해 None으로 설정
        if customSchemas is None:
            customSchemas = [None] * len(file_names)

        for file_name, customSchema in zip(file_names, customSchemas):
            df = self.loadTable(file_name, bucket=bucket, dpath=dpath, customSchema=customSchema, header=header, infer_schema=infer_schema)
            table_name = file_name.split('.')[0]  # Assuming the file name without extension is used as the table name
            df.createOrReplaceTempView(table_name)
            dataframes[table_name] = df

        return dataframes

    def queryTable(self, query, tableNames=None, bucket=None, dpath=None, customSchemas=None, header=True, infer_schema=True):
        self.logger.debug(("queryTable = ", query, tableNames))

        if tableNames is not None:
            self.loadTables(tableNames, bucket=bucket, dpath=dpath, customSchemas=customSchemas, header=header, infer_schema=infer_schema)

        json_df = self.spark.sql(query)

        return json_df

    def archive(self, file_name, bucket=None, dpath=None):
        self.logger.debug(("archive = ", file_name, bucket, dpath))
                
        sBucket = self._getBucket(bucket)
        sKey = self._getPath(file_name, dpath)
    
        archive_bucket = self.archive_bucket
        destination_key = self._getArchivePath(file_name, dpath)
        
        try:
            # Copy the file to the archive bucket
            self.s3_client.copy_object(CopySource={'Bucket': sBucket, 'Key': sKey },
                                       Bucket=archive_bucket,
                                       Key=destination_key)
                        
            # Verify that the copy was successful
            response = self.s3_client.head_object(Bucket=archive_bucket, Key=destination_key)
            if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                # If the copy was successful, delete the original file
                self.s3_client.delete_object(Bucket=sBucket, Key=sKey)

            self.logger.info(("Archived ", f"s3a://{sBucket}/{sKey} > s3a://{archive_bucket}/{destination_key}"))
        except Exception as e:
            self.logger.error("Error moving file to archive:", e)

    def _getBucket(self, bucket) :
        return self.default_bucket if bucket is None else bucket
    
    def _getPath(self, tableName, dpath=None) :
        if dpath is None:
            dpath = self.default_dpath
            
        return tableName if dpath is None else f'{dpath}/{tableName}'
    
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
