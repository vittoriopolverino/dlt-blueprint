from src.monitoring.data_quality_log import DataQualityLog
from src.pipelines.class_mapping import mapper as default_mapper
from src.monitoring.class_mapping import mapper as monitoring_mapper
from src.pipelines.sample_pipeline_1 import SamplePipeline1


def test_create_strategies_default(mock_pipeline_orchestrator):
    spark = mock_pipeline_orchestrator.spark
    pipelines = mock_pipeline_orchestrator.get_pipelines(execution_type='default')
    result = mock_pipeline_orchestrator.create_strategies(
        spark=spark,
        datalake_folder='abfss://container_name@datalake_name.dfs.core.windows.net/sample',
        pipelines=pipelines
    )

    expected_len = 2
    expected_instance = SamplePipeline1
    expected_spark_session = spark
    expected_table_name = 'sample_table'
    expected_primary_key = ['first_id', 'second_id']
    expected_cloudfiles_format = 'parquet'

    assert len(result) == expected_len
    assert isinstance(result[0], expected_instance)
    assert result[0].spark == expected_spark_session
    assert result[0].table_name == expected_table_name
    assert result[0].primary_key == expected_primary_key
    assert result[0].cloudfiles_format == expected_cloudfiles_format


def test_create_strategies_monitoring(mock_pipeline_orchestrator):
    spark = mock_pipeline_orchestrator.spark
    pipelines = mock_pipeline_orchestrator.get_pipelines(execution_type='monitoring')
    result = mock_pipeline_orchestrator.create_strategies(
        spark=spark,
        datalake_folder='abfss://container_name@datalake_name.dfs.core.windows.net/sample',
        pipelines=pipelines
    )

    expected_len = 1
    expected_instance = DataQualityLog
    expected_spark_session = spark
    expected_table_name = 'data_quality_log'
    expected_pipeline_ids = ['dlt_bronze', 'dlt_silver']
    expected_event_type = 'flow_progress'

    assert len(result) == expected_len
    assert isinstance(result[0], expected_instance)
    assert result[0].spark == expected_spark_session
    assert result[0].table_name == expected_table_name
    assert result[0].pipeline_ids == expected_pipeline_ids
    assert result[0].event_type == expected_event_type


def test_get_pipelines(mock_pipeline_orchestrator):
    result_default_pipelines = mock_pipeline_orchestrator.get_pipelines(execution_type='default')
    expected_default_pipelines = default_mapper

    result_monitoring_pipelines = mock_pipeline_orchestrator.get_pipelines(execution_type='monitoring')
    expected_monitoring_pipelines = monitoring_mapper

    assert result_default_pipelines == expected_default_pipelines
    assert result_monitoring_pipelines == expected_monitoring_pipelines

