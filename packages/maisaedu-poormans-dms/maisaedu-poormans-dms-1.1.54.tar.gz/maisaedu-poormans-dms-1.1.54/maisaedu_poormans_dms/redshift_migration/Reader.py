import io
import pandas as pd
from datetime import datetime
from .Types import (
    target_type_is_numeric,
    LOCAL,
    FULL,
    PROD,
    INCREMENTAL,
    SAVED_S3,
    PREFECT,
    S3,
)
from .Services.ExtractionOperation import ExtractionOperation
from .Services.AdapterSourceTarget import AdapterSourceTarget
from .Models.ExtractionOperation import ExtractionOperation as ExtractionOperationModel


class Reader:
    def __init__(self, s3_credentials, struct, migrator_redshift_connector):
        self.struct = struct
        self.s3_credentials = s3_credentials
        self.migrator_redshift_connector = migrator_redshift_connector

    def get_incremental_statement(self):
        if (
            (
                self.struct.source_incremental_column is not None
                and self.struct.target_incremental_column is not None
                and (self.load_option is None) 
            ) or (self.load_option == INCREMENTAL)
        ):
            sql = f"""
                select max("{self.struct.target_incremental_column}") as max_value
                from "{self.struct.target_schema}"."{self.struct.target_table}"
            """

            cursor = self.migrator_redshift_connector.target_conn.cursor()

            cursor.execute(sql)
            result = cursor.fetchall()

            if len(result) == 0 or result[0][0] is None:
                sql_return = ""
                self.load_option = FULL
            else:
                for c in self.struct.columns:
                    if c["target_name"] == self.struct.target_incremental_column:
                        target_type = c["target_type"]

                if target_type_is_numeric(target_type):
                    sql_return = f'and "{self.struct.source_incremental_column}" > {result[0][0]}'
                else:
                    if (
                        self.struct.incremental_interval_delta is None
                        or self.struct.incremental_interval_delta == ""
                    ):
                        sql_return = f"and \"{self.struct.source_incremental_column}\" > '{result[0][0]}'"
                    else:
                        sql_return = f"and \"{self.struct.source_incremental_column}\" >= '{result[0][0]}'::timestamp - interval '{self.struct.incremental_interval_delta}'"

                self.load_option = INCREMENTAL

            cursor.close()

            return sql_return
        else:
            if (self.load_option is None):
                self.load_option = FULL
            return ""

    def get_columns_source(self):
        return " * "

    def get_order_by_sql_statement(self):
        if self.struct.source_incremental_column is not None:
            return f' order by "{self.struct.source_incremental_column}" asc'
        else:
            return ""

    def get_limit_sql_statement(self):
        if self.migrator_redshift_connector.env == LOCAL:
            return f" limit 100"
        else:
            return f""

    def get_sql_statement(self):
        sql = f"""
            select {self.get_columns_source()} 
            from "{self.struct.source_schema}"."{self.struct.source_table}" 
            where 1=1
            {self.get_incremental_statement()} 
            {self.get_order_by_sql_statement()}
            {self.get_limit_sql_statement()}
        """
        return sql

    def save_on_bucket(self, df, path_file, format="parquet"):
        buffer = io.BytesIO()

        if format == "csv":
            df.to_csv(buffer, index=False)
        else:
            df.to_parquet(buffer, index=False, engine="pyarrow")
        self.migrator_redshift_connector.s3_session.Object(
            self.s3_credentials["bucket"],
            path_file,
        ).put(Body=buffer.getvalue())

        buffer.close()

    def save_data_to_s3(self, load_option=None):
        self.load_option = load_option
        self.migrator_redshift_connector.connect_s3()
        self.migrator_redshift_connector.connect_source()

        sql = self.get_sql_statement()

        time = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        idx = 1
        path_file = None

        for chunk_df in pd.read_sql(
            sql,
            self.migrator_redshift_connector.source_conn,
            chunksize=self.struct.read_batch_size,
        ):
            if len(chunk_df) != 0:
                path_file = f"raw/prefect/{self.migrator_redshift_connector.env}/{self.struct.target_schema}/{self.struct.target_table}/{time}/{idx}.parquet"
                path_file_tmp = f"raw/tmp/{self.migrator_redshift_connector.env}/{self.struct.target_schema}/{self.struct.target_table}/{time}/{idx}.csv"

                adapter = AdapterSourceTarget(self.struct)
                chunk_df_s3 = chunk_df.copy()

                chunk_df_s3 = adapter.transform_data(chunk_df_s3, target_save=S3)

                self.save_on_bucket(chunk_df_s3, path_file)

                chunk_df = adapter.convert_types(chunk_df)
                chunk_df = adapter.transform_data(chunk_df)
                chunk_df = adapter.equalize_number_columns(chunk_df)

                self.save_on_bucket(chunk_df, path_file_tmp, format="csv")
                idx = idx + 1

        self.migrator_redshift_connector.close_source()

        if path_file is None:
            return None
        else:
            url = f's3://{self.s3_credentials["bucket"]}/raw/prefect/{self.migrator_redshift_connector.env}/{self.struct.target_schema}/{self.struct.target_table}/{time}/'

            ExtractionOperation(
                conn=self.migrator_redshift_connector.target_conn,
            ).create(
                struct=self.struct,
                url=url,
                load_option=self.load_option,
                status=SAVED_S3,
                platform=self.struct.extraction_engine,
            )

            return ExtractionOperationModel(
                url=url,
                load_option=self.load_option,
            )
