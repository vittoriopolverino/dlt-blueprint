import pytest
from pyspark.sql import Column, DataFrame, SparkSession
from pyspark.sql.functions import count, first

from src.pipeline_orchestrator import Context
from tests.unit.sample_pipeline_test import SamplePipelineTest


@pytest.fixture(scope='session')
def mock_spark_session() -> SparkSession:
    return SparkSession.builder.getOrCreate()


@pytest.fixture()
def mock_pipeline(mock_spark_session) -> SamplePipelineTest:
    return SamplePipelineTest(
        spark=mock_spark_session, datalake_folder='abfss://container_name@datalake_name.dfs.core.windows.net/sample'
    )


@pytest.fixture()
def mock_primary_key() -> list[str]:
    return ['PK_ID']


@pytest.fixture()
def mock_primary_key_multiple_fields() -> list[str]:
    return ['FIRST_ID', 'SECOND_ID']


@pytest.fixture()
def mock_cloud_files_options() -> dict:
    return {
        'cloudFiles.format': 'parquet',
        'cloudFiles.useNotifications': 'false',
        'cloudFiles.schemaLocation': 'sample/schema_location_path',
    }


@pytest.fixture()
def mock_dataframe(mock_spark_session) -> DataFrame:
    return mock_spark_session.createDataFrame([{'a': 1, 'b': 2, 'c': 3}], schema=['a', 'b', 'c']).toDF('a', 'b', 'c')


@pytest.fixture()
def mock_aggregation_fields(mock_spark_session) -> list[Column]:
    return [
        first('a').alias('a'),
        first('b').alias('b'),
        first('c').alias('c'),
        count('*').alias('row_count'),
    ]


@pytest.fixture()
def mock_data_ingestions_log_dataframe(mock_spark_session) -> DataFrame:
    columns = ['table_name', 'status', 'last_updated_date', 'source_rows_count']
    data = [
        ('test_table', 'success', '2023-01-05 05:30:05.000', 300),
        ('test_table', 'success', '2023-01-06 05:30:05.000', 350),
        ('test_table', 'success', '2023-01-07 05:30:05.000', 500),
        ('test_table', 'success', '2023-01-08 05:30:05.000', 1000),
        ('test_table', 'success', '2023-01-09 05:30:05.000', 1450),
    ]
    return mock_spark_session.createDataFrame(data, columns)


@pytest.fixture()
def mock_context() -> Context:
    return Context()


@pytest.fixture()
def mock_class_name() -> dict:
    return {'sample_pipeline_test': SamplePipelineTest}
