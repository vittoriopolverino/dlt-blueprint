from dataclasses import dataclass, field

from pyspark.sql import SparkSession

from src.pipeline import Pipeline


@dataclass
class Contact(Pipeline):
    spark: SparkSession
    datalake_folder: str
    table_name: str = field(default='contact')
    primary_key: list[str] = field(default_factory=lambda: ['contactid'])
    cloudfiles_format: str = field(default='parquet')
    cloudfiles_schema_location: str = field(init=False, repr=True)
    cloud_files_options: dict[str, str] = field(init=False, repr=True)

    def __post_init__(self):
        self.cloudfiles_schema_location = f'{self.datalake_folder}/{self.table_name}/raw'
        self.cloud_files_options = super().get_cloud_files_options(
            file_format=self.cloudfiles_format,
            schema_location=self.cloudfiles_schema_location,
        )

    def raw_layer(self, **kwargs) -> None:
        super().raw_layer(**kwargs)

    def bronze_layer(self, **kwargs) -> None:
        datalake_folder = kwargs['datalake_folder']
        table_name = kwargs['table_name']
        primary_key = kwargs['primary_key']
        super().slowly_changing_dimensions_type_1(table_name=table_name, primary_key=primary_key)
        super().create_bronze_table(datalake_folder=datalake_folder, table_name=table_name, primary_key=primary_key)

    def silver_layer(self, **kwargs) -> None:
        pass

    def execute(self) -> None:
        # Initializes the raw layer
        self.raw_layer(
            spark=self.spark,
            datalake_folder=self.datalake_folder,
            table_name=self.table_name,
            cloud_files_options=self.cloud_files_options,
        )

        # Initializes the bronze layer
        self.bronze_layer(
            datalake_folder=self.datalake_folder,
            table_name=self.table_name,
            primary_key=self.primary_key,
        )
