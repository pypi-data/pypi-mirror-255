from pyspark.sql import SparkSession
from delta.tables import DeltaTable
from .pxlogger import CustomLogger
from .util import parseSourceObject
from pyspark.sql.window import Window
import pyspark.sql.functions as F
from pyspark.sql.functions import col
import urllib3
import warnings
import logging
import boto3

"""
Delta 테이블을 로드하고 저장하는 클래스

:param spark: Spark 세션.
:param default_bucket: Delta 테이블이 저장된 기본 S3 버킷.
:param default_dpath: Delta 테이블의 기본 dpath 또는 하위 디렉토리.
"""

class DeltaTableManager:
    
    def __init__(self, spark, bucket, dpath):
        self.spark = spark
        self.default_bucket = bucket
        self.default_dpath = dpath
        self.logger = CustomLogger("DeltaTableManager")
        self.dt_with_row = None
        self.tableName = None
        warnings.filterwarnings("ignore", category=FutureWarning)
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        s3_endpoint = spark._jsc.hadoopConfiguration().get("fs.s3a.endpoint")
        s3_access_key = spark._jsc.hadoopConfiguration().get("fs.s3a.access.key")
        s3_secret_key = spark._jsc.hadoopConfiguration().get("fs.s3a.secret.key")
        s3_ssl_verify = spark._jsc.hadoopConfiguration().get("fs.s3a.ssl.enabled")

        if s3_endpoint and s3_access_key and s3_secret_key :
            s3_ssl_verify = False if s3_ssl_verify is None else s3_ssl_verify
            self.s3_client = boto3.client('s3', endpoint_url=s3_endpoint, aws_access_key_id=s3_access_key, aws_secret_access_key=s3_secret_key, verify=s3_ssl_verify)


    def getType(self) :
        return "delta"
    
    def getTablePath(self, bucket, dpath, tableName):
        if bucket is None:
            bucket = self.default_bucket
        if dpath is None:
            dpath = self.default_dpath
            
        return f's3a://{bucket}/{tableName}' if dpath is None else f's3a://{bucket}/{dpath}/{tableName}'

 
    def load_table_with_row(self, tableName, target_table, customSchema=None):
        self.logger.debug(("load_table_with_row = ", self.tableName, tableName, target_table))

        if self.tableName == tableName and self.dt_with_row is not None:
            return self.dt_with_row
        else:
            if customSchema:
                # customSchema가 제공되면 해당 스키마를 사용하여 Delta 테이블을 로딩
                dt = self.spark.read.format("delta").schema(customSchema).load(target_table)
            else:
                # customSchema가 제공되지 않으면 기본 설정으로 Delta 테이블 로딩
                dt = self.spark.read.format("delta").load(target_table)

            # 'row_num' 열 생성
            window_spec = Window.orderBy(F.monotonically_increasing_id())
            self.dt_with_row = dt.withColumn("row_num", F.row_number().over(window_spec))
            self.tableName = tableName

        return self.dt_with_row
    
    def loadTable(self, tableName, offset=None, chunk_size=50000000, bucket=None, dpath=None, customSchema=None):        
        self.logger.debug(("loadTable = ", tableName, bucket, dpath, offset, chunk_size))

        target_table = self.getTablePath(bucket, dpath, tableName)
        self.logger.debug(("target_table = ", target_table))
        
        ## 매번 로딩인가?
        dt_with_row = self.load_table_with_row(tableName, target_table, customSchema)
        self.logger.debug(("dt_with_row size & offset = ", dt_with_row.count(), offset))

        if offset != None:
            dt_with_row_limit = dt_with_row.filter(f"row_num > {offset} AND row_num <= {offset + chunk_size}")
            self.logger.debug(("dt_with_row size limit = ", dt_with_row_limit.count(), dt_with_row.count()))
            dt_with_row_limit = dt_with_row_limit.drop("row_num")
            return dt_with_row_limit

        # offset 없는 경우 전체 로딩하고 spark SQL 의 테이블명 사용 지원
        dt_with_row = dt_with_row.drop("row_num")
        dt_with_row.createOrReplaceTempView(tableName)
        
        return dt_with_row
    
    def saveTable(self, dataFrame, tableName, bucket=None, dpath=None, mode="append", overwriteSchema=False, customSchema=None):
        self.logger.debug(("saveTable = ", tableName, bucket, dpath, mode, overwriteSchema, customSchema))
        table_path = self.getTablePath(bucket, dpath, tableName)

        before_count =  0

        # customSchema가 제공되면 해당 스키마를 사용하여 데이터를 저장
        if customSchema:
            dataFrame.write.format("delta").mode(mode).option("overwriteSchema", overwriteSchema).schema(customSchema).save(table_path)
        else:
            # 테이블이 이미 존재하는 경우에만 DELETE 실행
            if mode == "append" and DeltaTable.isDeltaTable(self.spark, table_path) :
                deltaTable = DeltaTable.forPath(self.spark, table_path)
                before_count = deltaTable.toDF().count()
            # customSchema가 제공되지 않으면 기본 설정으로 데이터를 저장
            dataFrame.write.format("delta").mode(mode).option("overwriteSchema", overwriteSchema).save(table_path)

        deltaTable = DeltaTable.forPath(self.spark, table_path)
        df = deltaTable.toDF()
        after_count = df.count()

        self.logger.debug(f"saveTable : before = {before_count}, after = {after_count} [ {tableName} ]")

        self.show_history(deltaTable, 1)

        return (after_count - before_count, df)
    

    def loadTables(self, tableNames, bucket=None, dpath=None, customSchemas=None):
        self.logger.debug(("loadTables = ", tableNames, bucket, dpath, customSchemas))

        tableNames = parseSourceObject(tableNames)
        dataframes = {}

        # customSchemas가 제공되지 않으면 모든 테이블에 대해 None으로 설정
        if customSchemas is None:
            customSchemas = [None] * len(tableNames)

        for tableName, customSchema in zip(tableNames, customSchemas):
            table_path = self.getTablePath(bucket, dpath, tableName)

            dt = None
            if DeltaTable.isDeltaTable(self.spark, table_path) is False :
                self.logger.error(f"loadTables : {table_path} is not delta table")
            if customSchema:
                # customSchema가 제공되면 해당 스키마를 사용하여 Delta 테이블을 로딩
                dt = self.spark.read.format("delta").schema(customSchema).load(table_path)
            else:
                # customSchema가 제공되지 않으면 기본 설정으로 Delta 테이블 로딩
                dt = self.spark.read.format("delta").load(table_path)

            dt.createOrReplaceTempView(tableName)
            dataframes[tableName] = dt

        return dataframes

    def queryTable(self, query, tableNames=None, bucket=None, dpath=None, customSchemas=None):
        self.logger.debug(("queryTable = ", query, tableNames, bucket, dpath, customSchemas))
 
        if tableNames is not None:
            self.loadTables(tableNames, bucket=bucket, dpath=dpath, customSchemas=customSchemas)
        
        delta_df = self.spark.sql(query)
        delta_df = delta_df.drop("row_num")

        return delta_df
    
    def delSert(self, dataFrame, condition, tableName, bucket=None, dpath=None, customSchema=None):
        self.logger.debug(("delSert = ", condition, tableName, bucket, dpath, customSchema))
        
        target_table = self.getTablePath(bucket, dpath, tableName)
        before_count =  del_count = 0
        
        # 테이블이 이미 존재하는 경우에만 DELETE 실행
        if DeltaTable.isDeltaTable(self.spark, target_table) :  
            deltaTable = DeltaTable.forPath(self.spark, target_table)
        
            before_count = deltaTable.toDF().count()
            
            if condition.lower().startswith("where "): 
                condition = condition[6:].lstrip()    # WHERE 시작인 경우 제거 

            # customSchema가 제공되면 해당 스키마를 사용하여 Delta 테이블을 로딩
            if customSchema:
                delta_df = deltaTable.toDF(schema=customSchema)
            else:
                delta_df = deltaTable.toDF()

            del_count = delta_df.filter(condition).count()
            
            deltaTable.delete(condition) 
 
        # customSchema가 제공되면 해당 스키마를 사용하여 데이터를 저장
        if customSchema:
            dataFrame.write.format("delta").mode("append").option("mergeSchema", "true").save(target_table)
        else:
            dataFrame.write.format("delta").mode("append").save(target_table)        
        
        deltaTable = DeltaTable.forPath(self.spark, target_table)
        df = deltaTable.toDF()
        after_count = df.count()
        
        self.logger.debug(f"delSert : before = {before_count}, after = {after_count}, del = {del_count} [ {target_table} / {condition} ]")
        
        self.show_history(deltaTable, 2)
        
        return (before_count, after_count, del_count, df)

    def countTableCondition(self, condition, tableName, bucket=None, dpath=None):
        target_table = self.getTablePath(bucket, dpath, tableName)
        if DeltaTable.isDeltaTable(self.spark, target_table) :  # 테이블이 이미 존재하는 경우에만 Query 실행
            deltaTable = DeltaTable.forPath(self.spark, target_table)
            if condition.lower().startswith("where "): 
                condition = condition[6:].lstrip()    # WHERE 시작인 경우 제거 
            count = deltaTable.toDF().filter(condition).count()    
            self.logger.debug(("target_table=", target_table, ", condition= ", condition, ", count=", count))
            return count
        return 0
        
    def getDeltaTable(self, tableName, bucket=None, dpath=None):
        target_table = self.getTablePath(bucket, dpath, tableName)
        return DeltaTable.forPath(self.spark, target_table)
        

    def _getLatestBeforeCount(self, tableName, bucket=None, dpath=None):
        target_table = self.getTablePath(bucket, dpath, tableName)
        deltaTable = DeltaTable.forPath(self.spark, target_table)

        # 최신 버전을 읽어오기 위해 versionAsOf 옵션을 사용
        latest_version = deltaTable.history().select("version").orderBy("version", ascending=False).first()["version"]

        # 최신 버전을 기준으로 Delta Table을 읽어오고 데이터 개수를 추출
        deltaTable_latest = deltaTable.versionAsOf(latest_version)
        before_count = deltaTable_latest.toDF().count()

        return before_count        
  
    # Delta Table의 파일 크기 확인 함수
    def getTableSize(self, tableName, bucket=None, dpath=None):
        delta_table_path = self.getTablePath(bucket, dpath, tableName)
        
        # Delta Table의 파일 크기를 저장할 변수
        table_size_bytes = 0

        # Delta Table의 경로에서 파일 목록을 가져옴
        file_list = self.spark._jvm.io.delta.tables.DeltaTable.forPath(self.spark._jvm.scala.collection.JavaConversions.asScalaBuffer([delta_table_path])).listFiles()

        # 파일 목록을 순회하면서 파일 크기를 누적
        for file_info in file_list:
            table_size_bytes += file_info.dataSize()

        # 바이트를 메가바이트로 변환
        table_size_mb = table_size_bytes / (1024 * 1024)  
        self.logger.debug((f"getTableSize ({delta_table_path}): {table_size_mb} MB "))

        return table_size_bytes

    def show_history(self, deltaTable, size=1):
        # deltaTable.history().select("version", "timestamp", "operation", "operationMetrics.executionTimeMs", 
        #                     "operationMetrics.numDeletedRows",
        #                     "operationMetrics.numOutputRows", "operationParameters").show(size, False)       

        if self.logger.getEffectiveLevel() != logging.DEBUG:
            return

        history_df = deltaTable.history().select(
            "version", "operation", "operationMetrics.numDeletedRows", "operationMetrics.numOutputRows", "operationParameters"
        )
        history_str = history_df.limit(size).toPandas().to_string(index=False, col_space=15)
        self.logger.debug("\n" + history_str)        


    def syncMeta(self, meta_df, tableName, bucket=None, dpath=None, src_topic=None):
        self.logger.debug(("syncMeta = ", tableName, bucket, dpath))

        delta_path = self.getTablePath(bucket, dpath, tableName)

        dbName = (dpath.split('/')[-1] if dpath is not None else None) if src_topic is None else src_topic
        dbName = dbName or self.default_dpath.split('/')[-1]

        table_info = meta_df.filter((col("db_name") == dbName) & (col("table_name") == tableName))

        if table_info.count() == 0:
            self.logger.debug(f"meta not found : {delta_path}")
            return table_info

        # table comments update
        table_comments = table_info.filter(col("column_name").isNull()).select("comments")
        column_comments = table_info.filter(col("column_name").isNotNull()).select(["column_name", "comments"])

        if table_comments.count() > 0 : 
            table_comment =  table_comments.first()[0]
            self.logger.debug(f"table meta update : '{delta_path}' comment = '{table_comment}'")
            tbl_query = f"alter table delta.`{delta_path}` set tblproperties ('comment' = '{table_comment}')"
            self.queryTable(tbl_query)

        for row in column_comments.collect():
            column_name = row['column_name']
            column_comments = row['comments']

            if column_name:
                # table column comments update 
                self.logger.debug(f"column meta update : '{delta_path}:{column_name}' comment = '{column_comments}'")
                col_query = f"ALTER TABLE delta.`{delta_path}` CHANGE COLUMN {column_name} COMMENT '{column_comments}'"
                self.queryTable(col_query)

        return table_info


    def listTables(self, bucket=None, dpath=None):
        if bucket is None:
            bucket = self.default_bucket
        if dpath is None:
            dpath = self.default_dpath

        dpath = dpath or ""
        delta_tables = self._list_deltas(bucket, dpath)

        #for delta_folder in delta_folders:
        #    if DeltaTable.isDeltaTable(self.spark, f's3a://{bucket}/{dpath}{delta_folder}'):
        #        delta_tables.append(top_folder)

        self.logger.debug(("listTables =", delta_tables))

        return delta_tables

    def _filter_delta(self, file_list) :
        top_level_folders = set()
        for file_path in file_list:
            components = file_path.split('/')
            if '_delta_log' in components:
                 # '_delta_log'를 포함하는 최상위 폴더를 찾기
                delta_log_index = components.index('_delta_log')
                top_folder = components[delta_log_index - 1]
                top_level_folders.add(top_folder)
        # set을 dictionary로 변환
        top_level_folders_dict = {folder: None for folder in top_level_folders}
        return top_level_folders_dict

    def _list_deltas(self, bucket_name, prefix):
        # 리스트를 저장할 빈 리스트를 생성합니다.
        files = {}
        continuation_token = None

        while True:
            params = {'Bucket': bucket_name, 'Prefix': prefix}
            if continuation_token:
                params['ContinuationToken'] = continuation_token

            response = self.s3_client.list_objects_v2(**params)

            sfiles = [obj['Key'] for obj in response.get('Contents', [])]
            deltas = self._filter_delta(sfiles)
            files.update(deltas)

            # 만약 페이징이 더 필요한 경우에는 루프를 계속합니다.
            if response.get('IsTruncated', False):
                continuation_token = response.get('NextContinuationToken')
            else:
                break

        return files 
