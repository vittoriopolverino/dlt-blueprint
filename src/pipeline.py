from abc import abstractmethod
from dataclasses import dataclass

from pyspark.sql import Column, DataFrame, SparkSession
from pyspark.sql.functions import (
    coalesce,
    col,
    count,
    first,
    input_file_name,
    lit,
    regexp_replace,
)

from src import logger

try:
    import dlt  # type: ignore
except ModuleNotFoundError:
    logger.logger.error('Module not found')


@dataclass
class Pipeline:
    """
    Abstract base class for pipelines.
    """

    @staticmethod
    def get_cloud_files_options(file_format: str, schema_location: str) -> dict[str, str]:
        """Generates a dictionary of options to use when reading or writing to Cloud Files.

        Args:
            file_format: A string representing the file format.
            schema_location: A string representing the location of the schema.

        Returns:
            A dictionary of options to use with Cloud Files.
        """
        return {
            'cloudFiles.format': file_format,
            'cloudFiles.useNotifications': 'false',
            'cloudFiles.schemaLocation': schema_location,
            # not supported yet
            # "cloudFiles.schemaEvolutionMode": "rescue"
        }

    @staticmethod
    def autoloader(
        spark: SparkSession,
        datalake_folder: str,
        table_name: str,
        cloud_files_options: dict[str, str],
    ) -> DataFrame:
        """Loads data from Cloud Files into a streaming view in Apache Spark.

        Args:
            - spark: An Apache Spark session.
            - datalake_folder: A string representing the name of the datalake folder
            - containing the data.
            - table_name: A string representing the name of the table whose data is being loaded.
            - cloud_files_options: A dictionary of options to use with Cloud Files.

        Returns:
            - Dataframe
        """
        return (
            spark.readStream.format('cloudFiles')
            .options(**cloud_files_options)
            .load(f'{datalake_folder}/{table_name}/raw')
            .drop('year', 'month', 'day', '_rescued_data')
            .withColumn('file_name', regexp_replace(regexp_replace(input_file_name(), '^.*Data/', 'Data/'), '%20', ' '))
        )

    @staticmethod
    def slowly_changing_dimensions_type_1(table_name: str, primary_key: list[str]) -> None:
        """
        Applies Slowly Changing Dimensions (SCD) Type 1

        Args:
        - table_name (str): the name of the table to apply SCD Type 1
        - primary_key (list[str]): the columns name list that make up the
        primary key of the table
        """

        dlt.create_streaming_live_table(
            name=f'scd1_{table_name}',
            table_properties={
                'quality': 'bronze',
            },
        )

        dlt.apply_changes(
            target=f'scd1_{table_name}',
            source=f'raw_{table_name}',
            keys=primary_key,
            sequence_by='modifiedon',
        )

    @staticmethod
    def create_pk_is_not_null_condition(primary_key: list[str]) -> str:
        """
        Generates a condition to checks that all primary key columns are
        not NULL.

        Args:
        - primary_key (list[str]): the list of names of the primary key columns

        Returns:
        - str: the condition to use in a WHERE clause
        """
        conditions = [f'{key} IS NOT NULL' for key in primary_key]
        return ' AND '.join(conditions)

    @staticmethod
    def create_group_by_field_list(dataframe: DataFrame, primary_key: list[str]) -> list[Column]:
        """
        Generates a list of fields to use in a GROUP BY clause based on the columns of a DataFrame
        and a list of primary key columns.

        Args:
        - df (DataFrame): the DataFrame whose columns to use
        - primary_key (list[str]): the list of names of the primary key columns

        Returns:
        - list[Column]: the list of fields to use in a GROUP BY clause
        """
        columns = dataframe.columns
        return [first(col).alias(col) for col in columns if col not in primary_key] + [count('*').alias('row_count')]

    @classmethod
    def check_duplicates_from_df(cls, dataframe: DataFrame, primary_key: list[str]) -> DataFrame:
        aggregation_fields = cls.create_group_by_field_list(dataframe=dataframe, primary_key=primary_key)
        duplicates_df = dataframe.groupBy(*primary_key).agg(*aggregation_fields).where(col('row_count') > 1)
        join_condition = [col('left.' + key) == col('right.' + key) for key in primary_key]

        return (
            dataframe.alias('left')
            .join(other=duplicates_df.alias('right'), on=join_condition, how='left')
            .select(
                col('left.*'),
                coalesce(col('right.row_count'), lit(1)).alias('row_count'),
            )
        )

    @classmethod
    def create_bronze_table(cls, datalake_folder: str, table_name: str, primary_key: list[str]) -> None:
        is_pk_not_null = cls.create_pk_is_not_null_condition(primary_key=primary_key)
        primary_key_str = ','.join(primary_key)
        is_pk_unique = 'row_count = 1'

        @dlt.table(
            name=f'bronze_{table_name}',
            path=f'{datalake_folder}/{table_name}/bronze',
            table_properties={'quality': 'bronze'},
        )
        @dlt.expect_all(
            {
                f'bronze bronze_{table_name} - not null {primary_key_str}': is_pk_not_null,
                f'bronze bronze_{table_name} - unique {primary_key_str}': is_pk_unique,
            }
        )
        def bronze_table():
            df = dlt.read(f'scd1_{table_name}')
            return cls.check_duplicates_from_df(dataframe=df, primary_key=primary_key)

    @classmethod
    def create_silver_table(
        cls, datalake_folder: str, table_name: str, primary_key: list[str]
    ) -> None:
        is_pk_not_null = cls.create_pk_is_not_null_condition(primary_key=primary_key)
        primary_key_str = ','.join(primary_key)
        is_pk_unique = 'row_count = 1'

        @dlt.table(
            name=f'silver_{table_name}',
            path=f'{datalake_folder}/{table_name}/silver',
            table_properties={'quality': 'silver'},
        )
        @dlt.expect_all(
            {
                f'silver silver_{table_name} - not null {primary_key_str}': is_pk_not_null,
                f'silver silver_{table_name} - unique {primary_key_str}': is_pk_unique,
            }
        )
        def silver_table():
            df = dlt.read(f'bronze_{table_name}').drop('row_count', 'file_name')
            return cls.check_duplicates_from_df(dataframe=df, primary_key=primary_key)

    @abstractmethod
    def raw_layer(self, **kwargs) -> None:
        spark = kwargs['spark']
        datalake_folder = kwargs['datalake_folder']
        table_name = kwargs['table_name']
        cloud_files_options = kwargs['cloud_files_options']

        @dlt.table(name=f'raw_{table_name}', table_properties={'quality': 'raw'}, temporary=True)
        def streaming_raw():
            return self.autoloader(
                spark=spark,
                datalake_folder=datalake_folder,
                table_name=table_name,
                cloud_files_options=cloud_files_options,
            )

    @abstractmethod
    def bronze_layer(self, **kwargs) -> None:
        """
        Creates the bronze layer

        Args:
        - datalake_folder (str): the name of the datalake folder containing the data
        - table_name (str): the name of the table to create in the bronze layer
        - primary_key (list[str]): the list of names of the primary key columns of the table
        """
        datalake_folder = kwargs['datalake_folder']
        table_name = kwargs['table_name']
        primary_key = kwargs['primary_key']

        self.slowly_changing_dimensions_type_1(table_name=table_name, primary_key=primary_key)
        self.create_bronze_table(datalake_folder=datalake_folder, table_name=table_name, primary_key=primary_key)

    @abstractmethod
    def silver_layer(self, **kwargs) -> None:
        datalake_folder = kwargs['datalake_folder']
        table_name = kwargs['table_name']
        primary_key = kwargs['primary_key']

        self.create_silver_table(
            datalake_folder=datalake_folder, table_name=table_name, primary_key=primary_key
        )

    @abstractmethod
    def execute(self) -> None:
        """Executes the process for creating the raw, bronze and silver layers
        Args:
        Returns: None

        """
        pass
