from .connection import Connection
from .s3_connection import S3Connection
from pyspark.sql import SparkSession
from pyspark.conf import SparkConf
from loguru import logger
import json


class SparkS3Connection(Connection):
    NAME = "spark_s3"

    def __init__(self) -> None:
        super().__init__()
        self.s3_connection: S3Connection = S3Connection()
        self.spark_session: SparkSession = SparkS3Connection.connect(self)

    def __create_spark_session__(self) -> SparkSession:
        if self.platform == self.__Platform__.LOCAL:
            conf = SparkConf()
            conf.set("spark.logConf", "true")
            spark = (
                SparkSession.builder.appName("BudgetGuard")
                .config(
                    "spark.jars",
                    "/opt/miniconda3/lib/python3.8/site-packages/pyspark/jars/aws-java-sdk-bundle-1.11.901.jar,/opt/miniconda3/lib/python3.8/site-packages/pyspark/jars/hadoop-aws-3.3.1.jar",  # noqa: E501
                )
                .getOrCreate()
            )
            spark = self.__build_local_spark_conf__(spark)
            spark.sparkContext.setLogLevel("ERROR")
        elif self.platform == self.__Platform__.EMR:
            spark = SparkSession.builder.appName("BudgetGuard").getOrCreate()
        else:
            raise Exception("Unknown platform!")
        return spark

    def connect(self) -> SparkSession:
        logger.info("Connecting to Spark session...")
        return self.__create_spark_session__()

    def __build_local_spark_conf__(self, spark: SparkSession) -> SparkSession:
        aws_credentials = json.loads(
            self.s3_connection.get_aws_secret("budget_guard_aws_credentials")
        )
        spark._jsc.hadoopConfiguration().set(
            "fs.s3a.access.key", aws_credentials["aws_access_key_id"]
        )
        spark._jsc.hadoopConfiguration().set(
            "fs.s3a.secret.key", aws_credentials["aws_secret_access_key"]
        )
        spark._jsc.hadoopConfiguration().set(
            "fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem"
        )
        spark._jsc.hadoopConfiguration().set(
            "com.amazonaws.services.s3.enableV4", "true"
        )
        spark._jsc.hadoopConfiguration().set(
            "fs.s3a.aws.credentials.provider",
            "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider",
        )
        spark._jsc.hadoopConfiguration().set(
            "fs.s3a.multiobjectdelete.enable", "false"
        )
        return spark
