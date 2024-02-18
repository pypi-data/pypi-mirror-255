from .pxlogger import CustomLogger
from pyspark.sql import SparkSession
from .spark_session import get_spark_session
from .resource_manager import ResourceManager
#from .order_manager import OrderManager
from .util import Timer
from .util import parseSourceObject
from .util import toCustomSchema
from functools import reduce
from pyspark.sql.functions import collect_list, struct, split
from pyspark.sql.functions import col, lit
from datetime import datetime
import time
import math


class EltManager:

    def __init__(self, spark, config_file="config.yaml", domain="",
            record_type=None, record_topic=None, record_dpath=None,
            skip_ingest_for_sucess_record=False, record_table="elt_manager_log", record_prefix=None): 

        self.spark = spark
        self.logger = CustomLogger("EltManager")
        #self.odm = OrderManager(spark)
        self.config_file = config_file
        self.domain = domain

        self.record = record_type is not None 
        self.record_full_header = "full" if record_prefix is None else record_prefix + "/full"
        self.record_inc_header = "inc" if record_prefix is None else record_prefix + "/inc"

        # 소스 타겟 대상 초기화 
        self.rsm = ResourceManager(self.spark, self.config_file)
        
        if self.record:
            self.record_tm = self.rsm.get_resource_manager(record_type, record_topic, dpath=record_dpath) #oracle
            self.record_table = record_table
            record_schema = {
                "record_time": "timestamp", "domain": "string", "action": "string",
                "source_type": "string", "source_topic": "string", "source_dpath": "string", "source_object": "string",
                "target_type": "string", "target_topic": "string", "target_dpath": "string", "target_object": "string",
                "valid": "boolean", "source_read_size": "long", "target_read_size": "long", "cleaned_count": "long",
                "error_message": "string", "elapsed": "float", }
            self.record_columns = toCustomSchema(record_schema)
            self.skip_ingest_for_sucess_record = skip_ingest_for_sucess_record

      
    def init_rsm(
        self,
        source_type, source_topic, source_dpath,
        target_type, target_topic, target_dpath,
        chunk_size=50000, lowercase=True):

        self.source_type = source_type
        self.source_topic = source_topic
        self.source_dpath = source_dpath
        self.target_type = target_type
        self.target_topic = target_topic
        self.target_dpath = target_dpath

        self.chunk_size = chunk_size
        self.lowercase = lowercase
    
        # 소스 대상 정의
        self.source_tm = self.rsm.get_resource_manager(source_type, source_topic, dpath=source_dpath) #oracle

        # 타셋 대상 정의
        self.target_tm = self.rsm.get_resource_manager(target_type, target_topic, dpath=target_dpath) #delta


    def _skip_ingest(self, action, source_object, target_object) :
        if self.record and self.skip_ingest_for_sucess_record:
            condition = f"source_topic='{self.source_topic}' and source_object='{source_object}' and target_object='{target_object}' and action='{action}' and valid" 
            count = self.record_tm.countTableCondition(condition, self.record_table)
            return count >= 1
        else :
            return False
            

    def _record(self, action, source_object, target_object, valid, source_read_size, target_read_size, cleaned_count, error_message, elapsed):
        if self.record:
            data = [(datetime.now(), self.domain, action, \
                     self.source_type, self.source_topic, self.source_dpath, source_object, \
                     self.target_type, self.target_topic, self.target_dpath, target_object, \
                     valid, source_read_size, target_read_size, cleaned_count, error_message, elapsed)]
            df = self.spark.createDataFrame(data, self.record_columns)
            self.record_tm.saveTable(df, self.record_table) #, mode="append")

        
    def getSourceManager(self) :
        return self.source_tm 
        
    def getTargetManager(self) :
        return self.target_tm
        
    def _getSourceInfo(self, source_objects) :
        return (
            f"{self.source_type} {self.source_topic} {self.source_dpath} {source_objects}"
            if self.source_dpath is not None
            else f"{self.source_type} {self.source_topic} _ {source_objects}"
        )
    
    def _getTargetInfo(self, target_object) :
        return (
            f"{self.target_type} {self.target_topic} {self.target_dpath} {target_object}"
            if self.target_dpath is not None
            else f"{self.target_type} {self.target_topic} _ {target_object}"
        )
    
    # Single tables full load
    def ingest_fulls(self, source_objects, target_object, source_customSchema=None, target_customSchema=None, count=True, offset=0, cleansing_conditions=None) :    
        sourceTables = parseSourceObject(tableNames)
        dataframes = {}

        for sourceTable in sourceTables: 
            (source_df, cleaned_target_df, valid) = self.ingest_full(sourceTable, target_object, sourceTables, sourceTables, count, offset, cleansing_conditions)
            dataframes[sourceTable] = (source_df, cleaned_target_df, valid)

        return dataframes        


    """
    This function ingests data from a source object to a target object with optional
    custom schemas, cleansing conditions, and other parameters.

    Parameters:
    - source_object (str): The source object or data file to ingest.
    - target_object (str): The target object or destination for ingested data.
    - source_customSchema (Optional[dict]): Custom schema for the source data (if applicable).
    - target_customSchema (Optional[dict]): Custom schema for the target data (if applicable).
    - count (bool): Flag to indicate whether to count the number of ingested records (default is True).
    - offset (int): Offset for starting ingestion from a specific record index (default is 0).
    - cleansing_conditions (Optional[dict]): Conditions for data cleansing (if applicable).
    - delimiter (Optional[str]): Delimiter used to separate fields in the data (only for cvs type).
    - charset (Optional[str]): Character set for encoding/decoding data (only for cvs type).
    - append_mode (bool): Flag to indicate whether to append data to the target (default is False: overwrite).

    Returns:
    - source_df (DataFrame): The DataFrame representing the source data after ingestion.
    - target_df (DataFrame): The DataFrame representing the target data after ingestion.
    - valid (bool): A boolean indicating the success of the ingestion process. True if successful, False otherwise.
    """    
    def ingest_full(self, source_object, target_object, 
            source_customSchema=None, target_customSchema=None, count=True, offset=0, 
            cleansing_conditions=None, append_mode=False, overwriteSchema=False, rebase_datetime=False,
            delemeter=None, charset=None, header=True):
        # 소스 > 타겟 Ingestion (chunk load)
        sourceTable = source_object[0] if isinstance(source_object, list) else source_object  # 단일 테이블에 대해서만 ingest_full 처리, 복수 테이블은 increment 기반 처리
        targetTable = target_object

        sourceInfo = self._getSourceInfo(source_object)
        targetInfo = self._getTargetInfo(target_object)

        timer = Timer()
        self.logger.info(f"ETL/FL Started : [ {targetInfo} ({source_object}) ]")

        source_df = None
        chunk_size = self.chunk_size

        target_df_org_count = 0

        try : 
            if rebase_datetime:
                self.spark.conf.set("spark.sql.parquet.int96RebaseModeInWrite", "LEGACY")

            if self.record and self._skip_ingest(self.record_full_header, sourceTable, target_object):
                self.logger.info(f"ETL/FL Skipped : [ {targetInfo} ({source_object}) ]")
                return (None, None, False)

            if append_mode :
                target_df = self.target_tm.loadTable(targetTable)
                if target_df is not None :
                    target_df_org_count = target_df.count()
                self.logger.info(f"Target count before append : {targetInfo} ({target_df_org_count:,})")

            if count is True:  # For RDBMS option
                source_df = self.source_tm.loadTable(sourceTable)

                if source_df is None :
                    raise RuntimeError(f"File not found: {sourceInfo} / {targetInfo}")

                size = source_df.count()

                if self.source_tm.getType() == "delta" and self.target_tm.getType() == "delta":
                    chunk_size = source_df.count()

                self.logger.info(f"Source count = {size:,} / expected loop {math.ceil(size / chunk_size)} / {timer.tab():.2f}")

            offset = offset
            chunk_read_size = chunk_size
            tot_cleaned_count = 0

            while chunk_read_size == chunk_size:

                # Oracle 데이터 읽기
                source_df = None
                if self.source_tm.getType() == "delta" and self.target_tm.getType() == "delta": # in case of delta to delta, we don't calculate row_num
                    source_df = self.source_tm.loadTable(sourceTable, offset=None, customSchema=source_customSchema)  # Full load
                elif self.source_tm.getType() == "csv":
                    source_df = self.source_tm.loadTable(sourceTable, offset=offset, chunk_size=chunk_size, customSchema=source_customSchema, delemeter=delemeter, charset=charset, header=header)
                else:
                    source_df = self.source_tm.loadTable(sourceTable, offset=offset, chunk_size=chunk_size, customSchema=source_customSchema)

                # 데이터가 없으면 종료
                if source_df is None :
                    raise RuntimeError(f"File not found: {sourceInfo} / {targetInfo}")

                #source_df.cache()

                cleaned_source_df = source_df
                if cleansing_conditions is not None:
                    cleaned_count, cleaned_source_df = self.cleansing(source_df, cleansing_conditions)
                    self.logger.info(f"Source  Cleaning : {sourceInfo} / cleaned_size={cleaned_count:,} / elipsed={timer.tab():.2f}")
                    tot_cleaned_count += cleaned_count

                # Save to Delta
                if offset == 0 and append_mode is not True:
                    # 컬럼 이름을 소문자로 변환
                    if self.lowercase is True:
                        cleaned_source_df = cleaned_source_df.toDF(*[col.lower() for col in cleaned_source_df.columns])

                    chunk_read_size, _ = self.target_tm.saveTable(cleaned_source_df, targetTable, mode="overwrite", overwriteSchema=overwriteSchema)
                else:
                    chunk_read_size, _ = self.target_tm.saveTable(cleaned_source_df, targetTable, mode="append", overwriteSchema=overwriteSchema)

                # 저장후 다시 읽음. 원천 데이터가 업데이트 시 크기가 더 클 수 있음
                # 저장 한 결과 기준으로 카운트 하고, 비교 필요
                #chunk_read_size = source_df.count()
                self.logger.info(f"Source Loading Chunk : {sourceInfo} / seq={math.ceil(offset / chunk_size + 1)} offset={offset:,} chunk_size={chunk_read_size:,} / elipsed={timer.tab():.2f}")

                self.logger.info(f"Target Saving Chunk : {targetInfo} / elipsed={timer.tab():.2f}")

                offset += chunk_read_size

                if self.source_tm.getType() in ["csv", "json"]:
                    self.source_tm.archive(sourceTable)
                    source_df.cache()  # For servicing after archiving

                if self.source_tm.getType() == "delta" and self.target_tm.getType() == "delta":  # Full loaded already
                    chunk_read_size = 0

            self.logger.info(f"Source Loading Count : {sourceInfo} ({offset:,})")

            target_df = self.target_tm.loadTable(targetTable)
            self.logger.info(f"Target Saving Count : {targetInfo} ({target_df.count():,})")

            valid = offset == target_df.count() + tot_cleaned_count - target_df_org_count

            self.logger.info(f"ETL/FL Done : [ {targetInfo} / {valid} ({offset:,}, {target_df.count() - target_df_org_count:,}, {tot_cleaned_count:,}) / {timer.elapsed():,.2f} ]")
            self._record(self.record_full_header, source_object, target_object, valid, offset, target_df.count(), tot_cleaned_count, None, timer.elapsed())

            if self.source_tm.getType() in ["csv", "json"]:
                source_df = self.source_tm.loadTable(sourceTable)

            return (source_df, target_df, valid)
        
        except Exception as e1:
            self.logger.error(f"ETL/FL Error : {e1}")
            self.logger.error(f"ETL/FL Done : [ {targetInfo} / False (-1, -1, -1) / {timer.elapsed():,.2f} ]")
            self._record(self.record_full_header, source_object, target_object, False, -1, -1, -1, str(e1)[:255], timer.elapsed())
            return (None, None, False)
        finally:
            if rebase_datetime:
                self.spark.conf.set("spark.sql.parquet.int96RebaseModeInWrite", "CORRECTED")
            

    """
    Incrementally ingests data from source objects to a target object based on specified conditions.

    Parameters:
    - source_objects (list): List of source objects or data files to incrementally ingest.
    - target_object (str): The target object or destination for incrementally ingested data.
    - source_inc_query (str): Incremental query or condition for selecting new data in the source.
    - target_condition (str): Condition for selecting existing data in the target for deleting.
    - source_df (Optional[DataFrame]): Optional DataFrame containing source data for incremental ingestion.
    - source_customSchema (Optional[dict]): Custom schema for the source data (if applicable).
    - target_customSchema (Optional[dict]): Custom schema for the target data (if applicable).
    - cleansing_conditions (Optional[dict]): Conditions for data cleansing (if applicable).
    - delimiter (Optional[str]): Delimiter used to separate fields in the data (only for csv type)
    - charset (Optional[str]): Character set for encoding/decoding data (only for csv type).

    Returns:
    - source_df (DataFrame): The DataFrame representing the source data after incremental ingestion.
    - target_df (DataFrame): The DataFrame representing the target data after merging.
    - valid (bool): A boolean indicating the success of the incremental ingestion process. True if successful, False otherwise.
    """
    def ingest_increment(self, source_objects, target_object, source_inc_query, target_condition,  
            source_df=None, source_customSchema=None, target_customSchema=None, cleansing_conditions=None, rebase_datetime=False,
            delemeter=None, charset=None, header=True) :    

        sourceInfo = self._getSourceInfo(source_objects)
        targetInfo = self._getTargetInfo(target_object)
        
        timer = Timer()
        self.logger.info(f"ETL/IC Started : [ {targetInfo} ({source_objects}) ]")

        try:
            if rebase_datetime:
                self.spark.conf.set("spark.sql.parquet.int96RebaseModeInWrite", "LEGACY")

            if source_df is None:
                if self.source_tm.getType() == "csv":
                    source_df = self.source_tm.queryTable(source_inc_query, tableNames=source_objects, customSchemas=source_customSchema, delemeter=delemeter, charset=charset, header=header)
                else:
                    source_df = self.source_tm.queryTable(source_inc_query, tableNames=source_objects, customSchemas=source_customSchema)

            # 데이터가 없으면 종료
            if source_df is None :
                raise RuntimeError(f"Source not found: {sourceInfo} / {targetInfo}")

            #source_df.cache()

            if target_customSchema:
                for column_name, data_type in target_customSchema.items():
                    source_df = source_df.withColumn(column_name, source_df[column_name].cast(data_type))

            cleaned_source_df = source_df
            cleaned_count = 0
            if cleansing_conditions is not None:
                cleaned_count, cleaned_source_df = self.cleansing(source_df, cleansing_conditions)
                self.logger.info(f"Source  Cleaning : {sourceInfo} / cleaned_size={cleaned_count:,} / elipsed={timer.tab():.2f}")

            # Save to Delta Incrementally
            before_count, after_count, del_count, target_df = self.target_tm.delSert(cleaned_source_df, target_condition, target_object)

            source_read_size = source_df.count()
            self.logger.info(f"Source Loading : {sourceInfo} / source_size={source_read_size:,} / elipsed={timer.tab():.2f}")

            self.logger.info(f"Target  Saving : {targetInfo} / delsert_size={after_count - before_count + del_count:,} (before={before_count:,}, after={after_count:,}, del={del_count:,}) / elipsed={timer.tab():.2f}")

            target_read_size = self.target_tm.countTableCondition(target_condition, target_object)
            valid = source_read_size == target_read_size + cleaned_count
            self.logger.info(f"ETL/IC Done : [ {targetInfo} / {valid} ({source_read_size:,}, {target_read_size:,}, {cleaned_count:,}) / {timer.elapsed():,.2f} ]")
            self._record(self.record_inc_header, source_objects, target_object, valid, source_read_size, target_read_size, cleaned_count, None, timer.elapsed())

            if self.source_tm.getType() in ["csv", "json"]:
                for sourceTable in source_objects:
                    self.source_tm.archive(sourceTable)        
                    source_df.cache()  # For servicing after archiving


            return (source_df, target_df, valid)
        
        except Exception as e1:
            self.logger.error(f"ETL/IC Error : {e1}")
            self.logger.error(f"ETL/IC Done : [ {targetInfo} / False (-1, -1, -1) / {timer.elapsed():,.2f} ]")
            self._record(self.record_inc_header, source_objects, target_object, False, -1, -1, -1, str(e1)[:255], timer.elapsed())
            return (None, None, False)
        finally:
            if rebase_datetime:
                self.spark.conf.set("spark.sql.parquet.int96RebaseModeInWrite", "CORRECTED")
        
    # condition1 = ~col("aaa").like("%.%")
    # cleansing_condition = F.col("vehno").isNotNull()  # Null 아닌것만 저장
    # condition2 = col("bbb") != "xyz"
    def cleansing(self, target_df,  cleansing_conditions=None):
        if cleansing_conditions is None:
            return (0, target_df)

        cleaned_df = target_df.filter(cleansing_conditions)
        count = target_df.count() - cleaned_df.count()
        self.logger.debug(f"Cleansed count={count} (before={target_df}, after={cleaned_df})")

        return (count, cleaned_df)


    # src_topic : 참조할 소스의 topic 이름
    def sync_meta(self, target_objects=None, src_topic=None):
        sourceInfo = self._getSourceInfo("_")
        targetInfo = self._getTargetInfo("_")

        timer = Timer()
        self.logger.info(f"ETL/Meta Started : [ {targetInfo} ]")

        source_meta = self.source_tm.loadMeta()
        self.logger.info(f"Source Meta Loading : {sourceInfo} / elipsed={timer.tab():.2f}")

        count = 0
        tables = self.target_tm.listTables() if target_objects is None else target_objects
        self.logger.info(f"Target Tables Loading : {targetInfo}  / elipsed={timer.tab():.2f}")
        for table in tables:
            targetInfo = self._getTargetInfo(table)
            meta_df = self.target_tm.syncMeta(source_meta, table, src_topic=src_topic)
            if meta_df.count() > 0 :
                count += 1
                self.logger.info(f"Target Meta Syncing : {targetInfo}  / elipsed={timer.tab():.2f}")
            else:
                self.logger.info(f"Target Meta Skipping : {targetInfo}  / elipsed={timer.tab():.2f}")

        targetInfo = self._getTargetInfo("_")
        self.logger.info(f"ETL/Meta Done : [ {targetInfo} / True ({count}, {count}) / {timer.elapsed():.2f} ]")


# from lib.elt_manager import EltManager
# em = EltManager(spark)        
#
# (Bronze Config)
# source_type = "oracle"
# source_topic = "bcparking"
# source_objects = ["tb_tminout"]
# target_type = "delta"
# target_topic = "bronze-bcparking"
# target_object = "tb_tminout"
#
# (Bronze Full Load)
# em.init_rsm(source_type, source_topic, target_type, target_topic, 500000)
# source_df, target_df = em.ingest_full(source_objects, target_object)
#
# (Bronze Incremental Load)
# source_inc_query = """
#     SELECT * FROM BCPARKING.TB_TMINOUT 
#     WHERE IN_DTTM < TO_DATE('2023-06-02', 'YYYY-MM-DD')
#     -- WHERE IN_DTTM >= TO_DATE('2023-06-02','YYYY-MM-DD') AND IN_DTTM < TO_DATE('2023-06-03','YYYY-MM-DD')
# """
# target_condition = "`IN_DTTM` < DATE '2023-06-02'"
# source_df, target_df = em.ingest_increment(source_objects, target_object, source_inc_query, target_condition)
#
# (Mart Config)
# source_type = "delta"
# source_topic = "gold"
# source_objects = ["tb_tminout"]
# target_type = "postgresql"
# target_topic = "mart"
# target_object = "public.tb_tminout"
#
# (Bronze Full Load)
# em.init_rsm(source_type, source_topic, target_type, target_topic, 500000)
# source_df, target_df = em.ingest_full(source_objects, target_object)
#
# (Incremental Load)
# source_inc_query = """
#     SELECT * FROM tb_tminout 
#     WHERE IN_DTTM < DATE '2023-06-02'
# """ 
# target_condition = "`IN_DTTM` < DATE '2023-06-02'"
# source_df, target_df = em.ingest_increment(source_objects, target_object, source_inc_query, target_condition)

                                
