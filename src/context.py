from dataclasses import dataclass, field
from typing import Union

from pyspark.sql import SparkSession

from src import logger
from src.bronze.class_mapping import class_name as bronze_class_name
from src.monitoring.class_mapping import class_name as monitoring_class_name
from src.pipeline import Pipeline
from src.silver.class_mapping import class_name as silver_class_name


@dataclass
class Context:
    """
    Context class that uses a strategy pattern to execute a specific set of functions based
    on the value of the 'layer' configuration setting.
    """

    spark: SparkSession = field(default_factory=lambda: SparkSession.builder.getOrCreate())
    scope_name: str = field(default='data-platform')
    container_name: str = field(default='ext-sources')
    datalake_folder: str = field(init=False, repr=True)
    layer: str = field(init=False, repr=True)
    class_name: dict[str, Union[Pipeline, str]] = field(init=False, repr=True)
    strategies: list = field(init=False, repr=True)
    dbutils: dict[str, str] = field(init=False, repr=True)

    def __post_init__(self):
        self.layer = self.spark.conf.get('layer', 'unknown layer')
        self.dbutils = self.get_dbutils(self.spark, container_name=self.container_name, scope_name=self.scope_name)
        self.datalake_folder = self.dbutils['datalake_folder']
        self.class_name = self.get_class_name(self.layer)

    @staticmethod
    def get_dbutils(spark: SparkSession, scope_name: str, container_name: str) -> dict[str, str]:
        try:
            # When run in a pipeline, this package will exist
            from pyspark.dbutils import DBUtils  # type: ignore

            dbutils = DBUtils(spark)
            # Retrieve the datalake name and secrets for the container from Databricks Secrets
            datalake_name = dbutils.secrets.get(scope_name, 'data-databricks-datalake-dtlkname')

            return {
                'datalake_name': datalake_name,
                'datalake_folder': f'abfss://{container_name}@{datalake_name}' f'.dfs.core.windows.net/Data/dynamics',
            }
        except ModuleNotFoundError:
            logger.logger.error('Module DBUtils not found')
            return {'datalake_name': 'n/a', 'datalake_folder': 'n/a'}

    @staticmethod
    def get_class_name(layer: str) -> dict[str, Union[Pipeline, str]]:
        """
        Returns a dictionary containing the class names for the specified layer.

        If the specified layer is invalid, a dictionary with a single key-value pair is returned:
        "error": "unexpected value".
        """
        # Returns the class name for the specified layer,
        # or an error dictionary if the layer is invalid
        class_mapper: dict = {
            'bronze': bronze_class_name,
            'silver': silver_class_name,
            'data_quality': monitoring_class_name,
        }
        return class_mapper.get(layer, {'error': 'unexpected value'})

    @staticmethod
    def create_strategies(spark: SparkSession, class_name: dict, datalake_folder: str) -> list:
        """Create a list of strategy objects.

        This function creates a list of strategy objects based on the names and
        corresponding classes provided in the `class_names` dictionary. The `spark`
        attribute of each strategy object is set to `self.spark`, and the `datalake_folder`
        attribute is set to `self.datalake_folder`.

        Args:
            spark: spark session
            class_name: A dictionary where the keys are the names of the strategy
                classes, and the values are the class objects.
            datalake_folder:

        Returns:
            A list of strategy objects.
        """
        # Create a list of strategy objects by iterating over the values in the
        # class_names dictionary and instantiating each class with the `spark` and
        # `datalake_folder` arguments
        return [obj(spark=spark, datalake_folder=datalake_folder) for obj in class_name.values()]

    @staticmethod
    def execute_strategies(strategies: list) -> None:
        for strategy in strategies:
            strategy.execute()

    def load(self) -> None:
        """
        load the context.
        """
        self.strategies = self.create_strategies(
            spark=self.spark, datalake_folder=self.datalake_folder, class_name=self.class_name
        )
        self.execute_strategies(strategies=self.strategies)
