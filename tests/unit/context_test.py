from src.bronze.class_mapping import class_name as bronze_class_name
from src.monitoring.class_mapping import class_name as monitoring_class_name
from src.silver.class_mapping import class_name as silver_class_name
from tests.unit.sample_pipeline_test import SamplePipelineTest


def test_create_strategies(mock_context, mock_class_name):
    result = mock_context.create_strategies(
        spark=mock_context.spark,
        class_name=mock_class_name,
        datalake_folder='abfss://container_name@datalake_name.dfs.core.windows.net/sample',
    )
    expected_len = 1
    expected_instance = SamplePipelineTest
    expected_spark_session = mock_context.spark
    expected_table_name = 'sample_pipeline_test'
    expected_cloudfiles_format = 'parquet'

    assert len(result) == expected_len
    assert isinstance(result[0], expected_instance)
    assert result[0].spark == expected_spark_session
    assert result[0].table_name == expected_table_name
    assert result[0].cloudfiles_format == expected_cloudfiles_format


def test_get_class_name(mock_spark_session, mock_context):
    result_class_name_bronze = mock_context.get_class_name(layer='bronze')
    expected_class_name_bronze = bronze_class_name

    result_class_name_silver = mock_context.get_class_name(layer='silver')
    expected_class_name_silver = silver_class_name

    result_class_name_data_quality = mock_context.get_class_name(layer='data_quality')
    expected_class_name_data_quality = monitoring_class_name

    result_class_name_gold = mock_context.get_class_name(layer='gold')
    expected_class_name_gold = {'error': 'unexpected value'}

    assert result_class_name_bronze == expected_class_name_bronze
    assert result_class_name_silver == expected_class_name_silver
    assert result_class_name_data_quality == expected_class_name_data_quality
    assert result_class_name_gold == expected_class_name_gold
