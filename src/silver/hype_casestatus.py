from dataclasses import dataclass, field

from pyspark.sql import SparkSession

from src.pipeline import Pipeline


@dataclass
class HypeCasestatus(Pipeline):
    spark: SparkSession
    datalake_folder: str
    table_name: str = field(default='hype_casestatus')
    primary_key: list[str] = field(default_factory=lambda: ['hype_casestatusid'])

    def __post_init__(self):
        pass

    def raw_layer(self, **kwargs) -> None:
        pass

    def bronze_layer(self, **kwargs) -> None:
        pass

    def silver_layer(self, **kwargs) -> None:
        super().silver_layer(**kwargs)

    def execute(self) -> None:
        self.silver_layer(
            spark=self.spark,
            datalake_folder=self.datalake_folder,
            table_name=self.table_name,
            primary_key=self.primary_key,
        )
