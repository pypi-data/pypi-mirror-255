from pyspark.sql import SparkSession
from pyspark import SparkConf
import os

# Generate SparkSession
def get_spark_session(_appName="Default AppName") -> SparkSession:
    conf = SparkConf() \
        .setAppName(_appName)
    
    spark = SparkSession \
        .builder \
        .config(conf=conf) \
        .config("spark.sql.session.timeZone", "Asia/Seoul") \
        .getOrCreate()

    return spark


def set_env_variables(conf:SparkConf):
    S3_ACCESS_KEY = os.environ['s3a_access_key']
    S3_SECRET_KEY = os.environ['s3a_secret_key']
    S3_ENDPOINT = os.environ['s3a_endpoint']
    S3_SSL_ENABLED = os.environ['s3a_connection_ssl_enabled']

    
    ## S3 설정 
    conf.set("spark.hadoop.fs.s3a.connection.ssl.enabled", S3_SSL_ENABLED)
    conf.set("spark.hadoop.fs.s3a.access.key", S3_ACCESS_KEY)
    conf.set("spark.hadoop.fs.s3a.secret.key", S3_SECRET_KEY)
    conf.set("spark.hadoop.fs.s3a.endpoint", S3_ENDPOINT)
    #conf.set("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
    #conf.set("spark.hadoop.fs.s3a.path.style.access", True)
    #conf.set("spark.hadoop.fs.s3a.aws.credentials.provider", "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider")
    
    ## delta 설정
    #conf.set("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
    #conf.set("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
    
    ## java extra package 설정
    #conf.set("spark.driver.extraJavaOptions", "-Divy.cache.dir={dir} -Divy.home={dir}".format(dir=JAVA_EXTRA_PACKAGE_DIR))
    #conf.set("spark.jars.packages", ",".join(JAVA_JAR_PACKAGE))
    
    ## standalone spark 연계
    #conf.set("spark.driver.host", SPARK_LOCAL_IP)
    #conf.set("spark.driver.cores", SPARK_DRIVER_CORES)    
    #conf.set("spark.driver.memory", SPARK_DRIVER_MEMORY)
    #conf.set("spark.executor.cores", SPARK_EXECUTOR_CORES)    
    #conf.set("spark.executor.memory", SPARK_EXECUTOR_MEMORY)
    #conf.set("spark.cores.max", SPARK_CORES_MAX)
    #if "http" in SPARK_PROXY_URL:
    #    conf.set("spark.ui.reverseProxy", True)
    #    conf.set("spark.ui.reverseProxyUrl", SPARK_PROXY_URL)

    # os.environ['oracle_driver']
    # os.environ['oracle_url']
    # os.environ['oracle_user']
    # os.environ['oracle_password']
   
    print("set conf OK! ")
