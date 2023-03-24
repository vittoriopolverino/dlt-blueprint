from dataclasses import dataclass, field

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lit

from src import logger
from src.pipeline import Pipeline

try:
    import dlt  # type: ignore
except ModuleNotFoundError:
    logger.logger.error('Module not found')


@dataclass
class MyPipeline(Pipeline):
    spark: SparkSession
    datalake_folder: str
    table_name: str = field(default='my_pipeline')
    primary_key: list[str] = field(default_factory=lambda: ['hype_casestatusid'])
    cloudfiles_format: str = field(default='parquet')
    cloudfiles_schema_location: str = field(init=False, repr=True)
    cloud_files_options: dict[str, str] = field(init=False, repr=True)

    def __post_init__(self):
        self.cloudfiles_schema_location = f'{self.datalake_folder}/{self.table_name}/raw'
        self.cloud_files_options = super().get_cloud_files_options(
            file_format=self.cloudfiles_format,
            schema_location=self.cloudfiles_schema_location,
        )

    @classmethod
    def create_bronze_table(cls, datalake_folder: str, table_name: str, primary_key: list[str]) -> None:
        is_pk_not_null = cls.create_pk_is_not_null_condition(primary_key=primary_key)
        primary_key_str = ','.join(primary_key)
        is_pk_unique = 'row_count = 1'

        @dlt.table(
            name=table_name,
            path=f'{datalake_folder}/{table_name}/bronze',
            table_properties={'quality': 'bronze'},
        )
        @dlt.expect_all(
            {
                f'bronze {table_name} - not null {primary_key_str}': is_pk_not_null,
                f'bronze {table_name} - unique {primary_key_str}': is_pk_unique,
            }
        )
        def bronze_table():
            # Reads the data from the SCD Type 1 table for the given table
            df = (
                dlt.read(f'scd1_{table_name}')
                .withColumn('pippo', lit(1))
                .withColumnRenamed('pippo', 'pippo_renamed')
                .withColumn('pippo_renamed', col('pippo_renamed').cast('double'))
            )
            return super(MyPipeline, cls).check_duplicates_from_df(dataframe=df, primary_key=primary_key)

    def raw_layer(self, **kwargs) -> None:
        super().raw_layer(**kwargs)

    def bronze_layer(self, **kwargs) -> None:
        datalake_folder = kwargs['datalake_folder']
        table_name = kwargs['table_name']
        primary_key = kwargs['primary_key']

        super().slowly_changing_dimensions_type_1(table_name=table_name, primary_key=primary_key)
        self.create_bronze_table(datalake_folder=datalake_folder, table_name=table_name, primary_key=primary_key)

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
            spark=self.spark,
            datalake_folder=self.datalake_folder,
            table_name=self.table_name,
            primary_key=self.primary_key,
        )
