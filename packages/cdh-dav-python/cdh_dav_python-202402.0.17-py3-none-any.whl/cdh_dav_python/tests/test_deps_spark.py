import os
import unittest
from pyspark.sql import SparkSession
from pyspark.sql.functions import lit, concat_ws, col
from datetime import datetime


class TestSpark(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.spark_generic = SparkSession.builder.appName("UnitTest").getOrCreate()
        running_local = True
        spark = None
        data_product_id = "cdh_premier"
        environment = "prod"
        cls.spark_connect_cpp = cls.get_spark_connect(
            running_local, spark, data_product_id, environment
        )

    def test_spark_connect_cpp_create_data_frame(self):
        # Sample data to mimic the file content
        data = [("cdh_unit_test", "view1"), ("cdh_unit_test", "view2")]
        schema = "data_product_id string, view_name string"
        df = self.spark_connect_cpp.createDataFrame(data, schema)

        # Configuration and other variables
        ingesttimestamp = datetime.now()
        data_product_id = "cdh_unit_test"

        # Transformation logic (mimicking your provided code)
        transformed_df = df.withColumn(
            "meta_ingesttimestamp", lit(ingesttimestamp)
        ).withColumn(
            "row_id",
            concat_ws("-", col("data_product_id"), col("view_name")),
        )
        transformed_df = transformed_df.filter(
            "data_product_id == '" + data_product_id + "'"
        )

        # Assertions
        result = transformed_df.collect()
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["data_product_id"], "cdh_unit_test")
        self.assertEqual(result[0]["row_id"], "cdh_unit_test-view1")

    def test_spark_connect_cpp_data_read_csv_from_cdh_premier_adls_prod(self):
        adls_csv_folder_path = "abfss://cdh@edavsynapsedatalake.dfs.core.windows.net/work/premier/prod/config/cdh/"
        adls_csv_file_path = f"{adls_csv_folder_path}bronze_sps_config_pipelines.csv"

        print(f"adls_csv_file_path:{adls_csv_file_path}")
        # Read the CSV file from ADLS
        df = (
            self.spark_connect_cpp.read.format("csv")
            .option("header", "true")
            .option("inferSchema", "true")
            .load(adls_csv_file_path)
        )

        # Configuration and other variables
        ingesttimestamp = datetime.now()
        data_product_id = "cdh_premier"

        # Transformation logic (mimicking your provided code)
        transformed_df = df.withColumn(
            "meta_ingesttimestamp", lit(ingesttimestamp)
        ).withColumn(
            "row_id",
            concat_ws("-", col("data_product_id"), col("view_name")),
        )
        transformed_df = transformed_df.filter(
            "data_product_id == '" + data_product_id + "'"
        )

        # Assertions
        result = transformed_df.collect()
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["data_product_id"], "abc")
        self.assertEqual(result[0]["row_id"], "abc-view1")

    def test_spark_generic_create_data_frame(self):
        # Sample data to mimic the file content
        data = [("cdh_unit_test", "view1"), ("cdh_unit_test", "view2")]
        schema = "data_product_id string, view_name string"
        df = self.spark_generic.createDataFrame(data, schema)

        # Configuration and other variables
        ingesttimestamp = datetime.now()
        data_product_id = "cdh_unit_test"

        # Transformation logic (mimicking your provided code)
        transformed_df = df.withColumn(
            "meta_ingesttimestamp", lit(ingesttimestamp)
        ).withColumn(
            "row_id",
            concat_ws("-", col("data_product_id"), col("view_name")),
        )
        transformed_df = transformed_df.filter(
            "data_product_id == '" + data_product_id + "'"
        )

        # Assertions
        result = transformed_df.collect()
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["data_product_id"], "cdh_unit_test")
        self.assertEqual(result[0]["row_id"], "cdh_unit_test-view1")

    def test_spark_generic_data_read_csv_from_cdh_premier_adls_prod(self):
        adls_csv_path = "abfss://[path-to-your-csv-in-adls]"

        # Read the CSV file from ADLS
        df = (
            self.spark_generic.read.format("csv")
            .option("header", "true")
            .option("inferSchema", "true")
            .load(adls_csv_path)
        )

        # Configuration and other variables
        ingesttimestamp = datetime.now()
        data_product_id = "cdh_premier"

        # Transformation logic (mimicking your provided code)
        transformed_df = df.withColumn(
            "meta_ingesttimestamp", lit(ingesttimestamp)
        ).withColumn(
            "row_id",
            concat_ws("-", col("data_product_id"), col("view_name")),
        )
        transformed_df = transformed_df.filter(
            "data_product_id == '" + data_product_id + "'"
        )

        # Assertions
        result = transformed_df.collect()
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["data_product_id"], "abc")
        self.assertEqual(result[0]["row_id"], "abc-view1")

    @classmethod
    def tearDownClass(cls):
        # cls.spark.stop()
        print("not_implemented")
