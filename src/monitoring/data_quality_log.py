from dataclasses import dataclass, field
from functools import reduce

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import col

from src import logger
from src.pipeline import Pipeline

try:
    import dlt  # type: ignore
except ModuleNotFoundError:
    logger.logger.error('Module not found')


@dataclass
class DataQualityLog(Pipeline):
    spark: SparkSession
    datalake_folder: str
    table_name: str = field(default='data_quality_log')
    pipeline_ids: list[str] = field(default_factory=lambda: ['dlt_bronze', 'dlt_silver'])
    event_type: str = 'flow_progress'

    def __post_init__(self):
        pass

    @staticmethod
    def wrk_data_quality_log(spark: SparkSession, table_name: str, pipeline_ids: list[str], event_type: str) -> None:
        @dlt.table(name=f'wrk_{table_name}', table_properties={'quality': 'bronze'}, temporary=True)
        def bronze_table():
            paths = [f'dbfs:/pipelines/{pipeline_id}/system/events' for pipeline_id in pipeline_ids]
            datframes = list(
                map(lambda path: spark.read.format('delta').load(path).where(col('event_type') == event_type), paths)
            )
            data_quality_log = reduce(DataFrame.union, datframes)
            return data_quality_log

    def raw_layer(self, **kwargs) -> None:
        pass

    def bronze_layer(self, **kwargs) -> None:
        spark = kwargs['spark']
        table_name = kwargs['table_name']

        self.wrk_data_quality_log(
            spark=self.spark, table_name=self.table_name, pipeline_ids=self.pipeline_ids, event_type=self.event_type
        )

        @dlt.table(name=table_name, table_properties={'quality': 'bronze'})
        def bronze_table():
            data_quality_log = spark.sql(
                """
                SELECT
                  row_expectations.dataset as dataset,
                  CASE
                    WHEN LOWER(row_expectations.name) LIKE '%bronze%' THEN 'bronze'
                    WHEN LOWER(row_expectations.name) LIKE '%silver%' THEN 'silver'
                    ELSE 'n/a'
                  END AS layer,
                  row_expectations.name as expectation,
                  substring(row_expectations.name, locate("-", row_expectations.name) + 1, len(row_expectations.name))
                  as expectation_short,
                  execution_date,
                  if(SUM(row_expectations.failed_records) = 0, 'passed', 'failed') as status,
                  SUM(row_expectations.passed_records) as passing_records,
                  SUM(row_expectations.failed_records) as failing_records
                FROM
                  (
                    SELECT
                      explode(from_json(
                          details :flow_progress :data_quality :expectations,
                          "array<struct<name: string, dataset: string, passed_records: int, failed_records: int>>"
                        )
                      ) row_expectations,
                      to_date(timestamp) as execution_date
                    FROM
                      LIVE.wrk_data_quality_log
                    WHERE
                      event_type = 'flow_progress'
                  )
                GROUP BY
                  row_expectations.dataset,
                  row_expectations.name,
                  substring(row_expectations.name, locate("-", row_expectations.name) + 1, len(row_expectations.name)),
                  execution_date
                  order by 1 """
            )
            return data_quality_log

    def silver_layer(self, **kwargs) -> None:
        pass

    def execute(self):
        self.bronze_layer(spark=self.spark, table_name=self.table_name)
