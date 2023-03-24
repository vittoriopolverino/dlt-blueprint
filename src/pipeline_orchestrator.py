from dataclasses import dataclass, field

from pyspark.sql import SparkSession

from src import logger
from src.pipelines.class_mapping import mapper as default_mapper
from src.monitoring.class_mapping import mapper as monitoring_mappper
from src.pipeline import Pipeline


@dataclass
class PipelineOrchestrator:
    spark: SparkSession = field(default_factory=lambda: SparkSession.builder.getOrCreate())
    scope_name: str = field(default='sample-scope')
    container_name: str = field(default='sample-container')
    datalake_folder: str = field(init=False, repr=True)
    pipelines: dict[Pipeline] = field(init=False, repr=True)
    execution_type: str = field(init=False, repr=True)
    strategies: list = field(init=False, repr=True)

    def __post_init__(self):
        self.execution_type = self.spark.conf.get('execution_type', 'n/a')
        self.datalake_folder = self.get_datalake_folder(
            spark=self.spark,
            container_name=self.container_name,
            scope_name=self.scope_name
        )
        self.pipelines = self.get_pipelines(execution_type=self.execution_type)

    @staticmethod
    def get_datalake_folder(spark: SparkSession, scope_name: str, container_name: str) -> str:
        try:
            from pyspark.dbutils import DBUtils  # type: ignore
            dbutils = DBUtils(spark)
            datalake_name = dbutils.secrets.get(scope_name, 'data-databricks-datalake-dtlkname')
            return f'abfss://{container_name}@{datalake_name}.dfs.core.windows.net/sample-folder'
        except ModuleNotFoundError:
            logger.logger.error('Module DBUtils not found')
            return 'n/a'

    @staticmethod
    def get_pipelines(execution_type: str) -> dict[Pipeline]:
        class_mapper: dict = {
            'default': default_mapper,
            'monitoring': monitoring_mappper,
        }
        return class_mapper.get(execution_type)

    @staticmethod
    def create_strategies(spark: SparkSession, pipelines: dict[Pipeline], datalake_folder: str) -> list:
        return [pipeline(spark=spark, datalake_folder=datalake_folder) for pipeline in pipelines.values()]

    @staticmethod
    def execute_strategies(strategies: list) -> None:
        for strategy in strategies:
            strategy.execute()

    def start(self) -> None:
        self.strategies = self.create_strategies(
            spark=self.spark, datalake_folder=self.datalake_folder, pipelines=self.pipelines
        )
        self.execute_strategies(strategies=self.strategies)
