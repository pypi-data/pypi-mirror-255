import decimal
import json
import logging
import os
import platform
import re
import uuid
from datetime import datetime
from time import sleep
from typing import List, Optional, Union

import google.cloud.logging
import numpy as np
import pandas as pd
from google.cloud import (
    bigquery,
    bigquery_datatransfer,
    bigquery_datatransfer_v1,
    bigquery_storage,
)
from google.cloud.bigquery.enums import EntityTypes
from google.protobuf.field_mask_pb2 import FieldMask
from pytz import timezone

from npgbq.core.helper_phone_number_th import format_phone

from ..connectors.dtype_mapper import oracle_to_gbq

# from ..connectors.mssql import get_conn_mssql # disabled in 2.0.5
from ..connectors.postgres import get_conn_pg
from .log_table_schema import gbq_log_schema

bqstorageclient = bigquery_storage.BigQueryReadClient()


class NPGBQ:
    def __init__(self, project_id, gcp_service_account_path: Optional[str] = None):
        self.project_id = project_id
        self.path_json_key = gcp_service_account_path
        self.__add_environment()
        # var default
        self.__log_dataset = "data_log"
        self.__log_table = "logs"
        self.job_uuid = None
        self.dataset_id = None
        self.table_name = None
        # create client
        self.client = self.__get_bq_client()
        self.client_sq = self.__get_sq_client()

    def __add_environment(self):
        if self.path_json_key:
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = self.path_json_key

    def __get_bq_client(self):
        client = google.cloud.logging.Client(project=self.project_id)
        client.setup_logging(log_level=logging.INFO)
        return bigquery.Client(self.project_id)

    def __get_sq_client(self):
        return bigquery_datatransfer.DataTransferServiceClient()

    def create_sql_transform(
        self, project_id, dataset_name, tbl_raw, tbl_mid, config, blobname
    ):
        # We can do this using except(my_col) as well, but it will change the order of the column
        # this is the reason why I use this method
        tbl_obj = self.client.get_table(f"{project_id}.{dataset_name}.{tbl_raw}")
        sql = f"""create or replace table `{project_id}.{dataset_name}.{tbl_mid}` as
        select \n
        {self.generate_cols_sql(tbl_obj,config,blobname)}
        from `{project_id}.{dataset_name}.{tbl_raw}`
        ;
        """
        return sql

    def generate_cols_sql(self, tbl_obj: bigquery.Table, config: dict, blobname: str):
        cols = []
        for col in tbl_obj.schema:
            if col.name in config:
                col_config = config[col.name]
                cols.append(self.get_col_convert(col.name, col_config))
            else:
                cols.append(col.name)
        # add ingestion timestamp
        cols.append(f"'{blobname}' as src_blob")
        cols.append("current_timestamp() as ingestion_timestamp")
        return ",".join(cols)

    def get_col_convert(self, col_name, config: dict):
        if config["how"] == "timestamp_millis":
            return f"timestamp_millis({col_name}) as {col_name}"
        if config["how"] == "timestamp":
            return f"timestamp({col_name}) as {col_name}"
        if config["how"] == "string":
            dtype = config["how"]
            return f"CAST({col_name} AS {dtype}) as {col_name}"
        raise ValueError(f"{config['how']} is not valid for {col_name}")

    @staticmethod
    def get_valid_colname(text: str):
        val = re.sub("[^A-Za-z0-9_]+", "_", text)
        val = NPGBQ.remove_double_underscores(val)
        val = NPGBQ.remove_double_space(val)
        val = val.upper().rstrip("_").lstrip("_")
        if re.search(r"^\d", val):
            val = f"_{val}"
        return val

    @staticmethod
    def remove_double_space(text: str) -> str:
        regex = re.compile(r"\s+")
        return re.sub(regex, " ", text)

    @staticmethod
    def remove_double_underscores(text: str) -> str:
        regex = re.compile(r"__+")
        return re.sub(regex, "_", text)

    def format_deciaml_cols(self, df, col_decimal):
        for col in col_decimal:
            df[col] = df[col].astype(str).map(decimal.Decimal)
        return df

    def __validate_col_type(self, col_type: str) -> bool:
        valid_col_type = [
            "ARRAY",
            "BIGNUMERIC",
            "BOOL",
            "BOOLEAN",
            "DATE",
            "DATES",
            "FLOAT",
            "FLOAT64",
            "GEOGRAPHY",
            "INT64",
            "INTEGER",
            "INTERVAL",
            "NUMERIC",
            "STRING",
            "TIME",
            "TIMESTAMP",
        ]
        if col_type not in valid_col_type:
            raise ValueError(f"the input column datatype {  col_type} is not valid")
        return True

    @staticmethod
    def get_full_qualified_table_name(project_id, dataset_id, table_id):
        full_qualified_id = f"{project_id}.{dataset_id}.{table_id}"
        return full_qualified_id

    def __get_full_qualified_table_name(self, dataset_id, table_id):
        full_qualified_id = f"{self.client.project}.{dataset_id}.{table_id}"
        return full_qualified_id

    def update_schema(self, table_obj: bigquery.Table, mapping: dict, desc: str):
        """
        Usage:
        table_id = "central-cto-cds-data-hub-prd.rbs_mdc.customer_entity"
        table_obj = gbq.client.get_table(table_id)
        mapping = {"default_billing": "INTEGER", "default_shipping": "INTEGER",'gender':'INTEGER'}
        gbq.update_schema(table_obj, mapping)
        """
        schema = table_obj.schema
        _schema = []
        for field in schema:
            if field.name in mapping:
                new_field = bigquery.SchemaField(field.name, mapping[field.name], mode=field.mode, description=desc)  # type: ignore
                _schema.append(new_field)
            else:
                _schema.append(field)
        table_obj.schema = _schema
        self.client.update_table(table_obj, ["schema"])
        print(f"Schema updated for {table_obj.full_table_id}")

    def get_col_rename_dict(self, dict_org: dict, dict_gbq: dict) -> dict:
        res = {}
        for (k1, v2), (k2, v2) in zip(dict_org.items(), dict_gbq.items()):
            if k1 != k2:
                res[k1] = k2
        return res

    def __get_db_connection(
        self,
        db_hostname_or_ip,
        db_port_number,
        db_database_name,
        db_username,
        db_password,
        engine="postgres",
    ):
        # self.log2bq(message=f"Making connection to database: {db_database_name}")
        conn = None
        if engine == "postgres":
            conn = get_conn_pg(
                db_hostname_or_ip,
                db_port_number,
                db_database_name,
                db_username,
                db_password,
            )
        # disabled in 2.0.5
        # elif engine == "mssql":
        #     conn = get_conn_mssql(
        #         db_hostname_or_ip,
        #         db_port_number,
        #         db_database_name,
        #         db_username,
        #         db_password,
        #     )
        else:
            raise NotImplementedError(
                f"your engine {engine} is invalid please contact the administrator"
            )
        # self.log2bq(message=f"The connection is ready: {db_database_name}")
        return conn

    # ====================================== Public method ======================================

    def create_bq_dataset(self, dataset_id):
        try:
            dataset_id = f"{self.client.project}.{dataset_id}"
            dataset = bigquery.Dataset(dataset_id)
            dataset.location = "asia-southeast1"
            dataset = self.client.create_dataset(dataset, timeout=30)
        except Exception as e:
            print(f"Can not create the dataset: {e}")
        else:
            print(f"Created dataset name {dataset_id}")

    def get_dataset(self, dataset_id):
        try:
            dataset_id = f"{self.client.project}.{dataset_id}"
            dataset = self.client.get_dataset(dataset_id)
        except Exception as e:
            return None
        else:
            return dataset

    def remove_tables_from_dataset(self, dataset_name):
        tables = self.list_tables(dataset_name)
        for table in tables:
            table_name = table.split(".")[-1]
            self.delete_bq_table(dataset_name, table_name)

    def delete_bq_dataset(self, dataset_name: str = "DATASET_ABC"):
        dataset_name = f"{self.client.project}.{dataset_name}"
        self.client.delete_dataset(
            dataset_name, timeout=30, delete_contents=True, not_found_ok=True
        )
        print(f"Deleted dataset: {dataset_name}")

    def get_partition_type(self, ptype):
        if ptype.upper() == "DAY":
            return bigquery.TimePartitioningType.DAY
        if ptype.upper() == "HOUR":
            return bigquery.TimePartitioningType.HOUR
        raise NotImplementedError(f"The type {ptype} is not supported")

    def get_partition_config(self, config: dict):
        col_name = config.get("col_name")
        col_type = config.get("partition_type")
        time_partitioning = bigquery.TimePartitioning(
            field=col_name,  # specify the column to use for partitioning
            type_=self.get_partition_type(col_type),  # partition by day
            expiration_ms=None,  # never auto-expire partitions
        )
        return time_partitioning

    def add_pkey(self, full_table_id, columns):
        # you can add multiple columns to the pkey as well
        # full table_id e.g. myproject.mydataset.mytable
        cols = ", ".join(f"`{c}`" for c in columns)
        sql = f"""
        alter table `{full_table_id}`
        add primary key({cols})  not enforced
        ;
        """
        self.run_sql(sql)
        return sql

    def create_bq_table(
        self,
        dataset_id,
        table_id,
        schema,
        partition=False,
        partition_config=None,
        cluster_col=None,
        labels=None,
        kms_key_name=None,
    ):
        # sample value: parition_config: {"col_name": "MYCOL", "partition_type": "DAY"}
        # sample value: cluster_col: ["col1", "col2"]
        full_qualified_id = self.__get_full_qualified_table_name(dataset_id, table_id)
        table = bigquery.Table(full_qualified_id, schema=schema)
        # partition ref: https://cloud.google.com/bigquery/docs/partitioned-tables
        if partition and partition_config:
            table.time_partitioning = self.get_partition_config(partition_config)
        elif partition:
            # default partition by built-in _PARTITIONTIME column
            table.partitioning_type = "DAY"
        if cluster_col:
            table.clustering_fields = cluster_col
        if labels:
            table.labels = labels
        if kms_key_name:
            table.encryption_configuration = bigquery.EncryptionConfiguration(
                kms_key_name=kms_key_name
            )
        try:
            table = self.client.create_table(table)
        except Exception as e:
            print(f"Can not create table: {e}")
        else:
            print(f"Created the table name {table_id}")

    def get_primary_key(self, project_id, dataset_name, table_name):
        table_obj = self.client.get_table(f"{project_id}.{dataset_name}.{table_name}")
        const = table_obj._properties.get("tableConstraints")
        if const:
            return const["primaryKey"]["columns"]
        return None

    def list_views(self, project_id):
        sql = f"""
        SELECT
        *
        FROM (
        SELECT
            table_source,
            CONCAT(table_catalog,".",table_schema,".",view_name) AS view_name,
        FROM (
            SELECT
            table_catalog,
            table_schema,
            table_name AS view_name,
            view_definition AS query,
            ARRAY_CONCAT( REGEXP_EXTRACT_ALL(view_definition, r"[a-zA-Z0-9_-]+[.][a-zA-Z0-9_]+[.][a-zA-Z0-9_]+") ) AS table_source,
            FROM
            `{project_id}`.`region-asia-southeast1.INFORMATION_SCHEMA.VIEWS` ),
            UNNEST(table_source ) table_source)
        """
        df = self.get_data_from_gbq_2(sql)
        return df

    def grant_dataset_access(self, dataset_child, dataset_parent):
        # https://cloud.google.com/bigquery/docs/control-access-to-resources-iam#python
        # Construct a BigQuery client object.
        dataset = self.client.get_dataset(dataset_parent)
        role = None
        (
            dataset_require_authorized_project,
            dataset_require_authorized_dataset_id,
        ) = dataset_child.split(".")
        entries = list(dataset.access_entries)
        entries.append(
            bigquery.AccessEntry(
                role=role,
                entity_type=EntityTypes.DATASET,
                entity_id={
                    "dataset": {
                        "datasetId": dataset_require_authorized_dataset_id,
                        "projectId": dataset_require_authorized_project,
                    },
                    "targetTypes": ["VIEWS"],
                },
            )
        )
        dataset.access_entries = entries
        try:
            dataset = self.client.update_dataset(dataset, ["access_entries"])
            full_dataset_id = f"{dataset.project}.{dataset.dataset_id}"
            print(
                f"The dataset {dataset_child} is now authorized to query data from {dataset_parent}"
            )
        except Exception as e:
            print(str(e))

    def load_file_to_table(
        self,
        files: str,
        dataset_name: str,
        table_name: str,
        filetype: str = "csv",
        partition=False,
    ):
        # CSV
        config_csv = bigquery.LoadJobConfig()
        config_csv.source_format = bigquery.SourceFormat.CSV
        config_csv.skip_leading_rows = 1
        config_csv.autodetect = True
        # CSV with GZIP
        config_gzip = bigquery.LoadJobConfig()
        config_gzip.source_format = bigquery.SourceFormat.CSV
        config_gzip.skip_leading_rows = 1
        config_gzip.autodetect = True
        # AVRO
        config_avro = bigquery.LoadJobConfig()
        config_avro.source_format = bigquery.SourceFormat.AVRO
        # config_avro.autodetect = True
        # PARQUET
        config_parquet = bigquery.LoadJobConfig()
        config_parquet.source_format = bigquery.SourceFormat.PARQUET
        # config_parquet.autodetect=True
        configs = {
            "CSV": config_csv,
            "GZIP": config_gzip,
            "AVRO": config_avro,
            "PARQUET": config_parquet,
        }
        job_config = configs[filetype.upper()]
        # create table if not exists
        try:
            full_qualified_id = self.__get_full_qualified_table_name(
                dataset_name, table_name
            )
            table = bigquery.Table(full_qualified_id)
            if partition:
                table.partitioning_type = "DAY"
            table = self.client.create_table(table)
        except Exception as err:
            print(err)
        # load
        table_ref = self.client.dataset(dataset_name).table(table_name)
        job = self.client.load_table_from_uri(
            files,
            table_ref,
            job_config=job_config,
        )
        job.result()
        print(f"Loaded file {files} to the table {dataset_name}.{table_name}")

    def is_table_exists(self, project_id, dataset_id, table_id):
        table_id = f"{project_id}.{dataset_id}.{table_id}"
        try:
            self.client.get_table(table_id)
        except Exception as err:
            return False
        else:
            return True

    def insert_to_final_table(self, table_src_id, table_dst_id, table_config):
        project_id, dataset_name, table_name = table_dst_id.split(".")
        if self.is_table_exists(project_id, dataset_name, table_name):
            sql = self.get_simple_insert_sql(table_src_id, table_dst_id)
        else:
            sql = self.get_create_sql(table_src_id, table_dst_id, table_config)
        self.run_sql(sql)

    def get_simple_insert_sql(self, table_src_id, table_dst_id):
        # get the list of target columns then ensure to select the same number of columns
        tbl_src = self.client.get_table(table_src_id)
        tbl_dst = self.client.get_table(table_dst_id)
        cols = self.generate_valid_columns(tbl_src,tbl_dst) 
        sql = f"""INSERT INTO `{table_dst_id}`
        SELECT {cols} FROM `{table_src_id}`
        ;
        """
        return sql

    def generate_valid_columns(self,tbl_src:bigquery.Table,tbl_dst:bigquery.Table):
        cols_src = {c.name:c.field_type for c in tbl_src.schema}
        cols_dst = {c.name:c.field_type for c in tbl_dst.schema}
        cols = []
        for col_name,col_type in cols_dst.items():
            if col_name in cols_src:
                cols.append(self.get_col_same_type(col_name,col_type,cols_src[col_name]))
            else:
                cols.append(f"NULL as {c}")
        return ', '.join(f'{w}' for w in cols)
        

    def get_col_same_type(self,col_name,col_type_ep,col_type_in):
        # cast the column datatype if needed
        if col_type_ep != col_type_in:
            return f"CAST(`{col_name}` as {col_type_ep}) as {col_name}"
        return f"`{col_name}`"

    def get_create_sql(self, table_src_id, table_dst_id, table_config):
        partition_config = table_config["partition_col"]
        cluster_config = table_config["cluster_col"]
        sql = f"""CREATE TABLE `{table_dst_id}`
        PARTITION BY {self.get_partition_text(partition_config)}
        {self.get_cluster_text(cluster_config)}
        AS
        SELECT * FROM `{table_src_id}`
        ;
        """
        return sql

    def get_partition_text(self, partition_config):
        if partition_config:
            col_name = partition_config["name"]
            data_type = partition_config["type"]
            mode = partition_config["mode"]
            return self.format_partition_text(col_name, data_type, mode)
        else:
            # use ingestion_timestamp
            return "DATE(ingestion_timestamp)"

    def format_partition_text(self, col_name, data_type, mode):
        if data_type.lower() == "timestamp":
            if mode.lower() == "day":
                return f"DATE({col_name})"
            elif mode.lower() == "hour":
                return f"HOUR({col_name})"
            elif mode.lower() == "month":
                return f"MONTH({col_name})"
            else:
                raise ValueError(f"Invalid partition mode: {mode}")

    def get_cluster_text(self, cluster_config: list):
        if cluster_config:
            return f"CLUSTER BY {','.join(cluster_config)}"
        else:
            return ""

    def export_bq_to_gcs(
        self, sql, file_format, bucket_name, bucket_path, date_partition
    ):
        sql = f"""
        EXPORT DATA
        OPTIONS ( uri="gs://{bucket_name}/{bucket_path}/dt={date_partition}/*.{file_format}",
            format={file_format.upper()},
            OVERWRITE=TRUE,
            compression=SNAPPY) AS
        {sql}
        """
        self.run_sql(sql)
        print(f"Exported to {bucket_name}")

    def create_log_table(self):
        schema_dict = gbq_log_schema
        schema = self.generate_bq_schema_from_dict(schema_dict)
        self.create_bq_dataset(self.__log_dataset)
        self.create_bq_table(
            self.__log_dataset, table_id=self.__log_table, schema=schema
        )

    def create_backup_table(self, dataset_id, table_name):
        now_th = datetime.now(timezone("Asia/Bangkok"))
        now_th_text = now_th.strftime("%Y%m%d_%H%M%S")
        table_name_src = self.__get_full_qualified_table_name(
            dataset_id=dataset_id, table_id=table_name
        )
        table_name_backup = f"{table_name}_bkp_{now_th_text}"
        table_name_backup = self.__get_full_qualified_table_name(
            dataset_id=dataset_id, table_id=table_name_backup
        )
        sql = f"""
		CREATE TABLE `{table_name_backup}`
		AS SELECT * FROM `{table_name_src}`
		;
		"""
        self.run_sql(sql)

    def merge_table(self, dataset_id, table_src, table_dst, col_key, columns):
        table_src = self.__get_full_qualified_table_name(
            dataset_id=dataset_id, table_id=table_src
        )
        table_dst = self.__get_full_qualified_table_name(
            dataset_id=dataset_id, table_id=table_dst
        )
        on_key = self.generate_merge_on_key(col_key)
        col_update_set = self.generate_sql_merge_update_set(columns, col_key)
        col_insert_set = self.generate_sql_merge_insert_set(columns)
        sql = f"""
		MERGE `{table_dst}` as t
		USING `{table_src}` as s
			ON (
				{on_key}
			)
			WHEN MATCHED THEN
				UPDATE SET 
					{col_update_set}
			WHEN NOT MATCHED THEN
				{col_insert_set}
		"""
        self.run_sql(sql)

    def __get_is_nullable(self, args: str) -> str:
        # todo handle REPEATED type
        if args in ("Yes", "YES", "yes", "Y", "y"):
            return "NULLABLE"
        return "REQUIRED"

    def generate_dummy_schema_from_df(self, df: pd.DataFrame, output_path=None):
        data = {}
        for index, col in enumerate(df.columns):
            data[col] = {
                "data_type": "STRING",
                "precision": 0,
                "scale": 0,
                "is_nullable": "YES",
                "col_id": index,
                "description": "column description",
            }
        if output_path:
            with open(output_path, "w", encoding="utf8") as json_file:
                json.dump(data, json_file, ensure_ascii=False, indent=4)

    def read_schema_from_file(self, file_path: str) -> dict:
        with open(file_path, "r", encoding="utf8") as json_file:
            data = json.load(json_file)
        return data

    def generate_bq_schema_from_dict(
        self, schema_dict, add_etl_cols=False, add_etl_filename=False
    ):
        """
        Example:
        {
            'column_name': {
                'data_type': 'STRING',
                'precision': 0,
                'scale': 0,
                'is_nullable': 'YES',
                'col_id': 1,
                'description': 'column description'
            },
            'column_name2': {
                'data_type': 'STRING',
                'precision': 0,
                'scale': 0,
                'is_nullable': 'YES',
                'col_id': 1,
                'description': 'column description'
            }
        }
        """
        schema = []
        for k, v in schema_dict.items():
            col_name = k
            col_type = v.get("data_type")
            col_mode = self.__get_is_nullable(v.get("is_nullable"))
            desc = v.get("description")
            schema.append(
                bigquery.SchemaField(
                    col_name, col_type, mode=col_mode, description=desc
                )
            )
        # add the etl extra columns if needed
        if add_etl_cols:
            if add_etl_filename:
                schema.append(
                    bigquery.SchemaField(
                        "etl_sourcefilename", "STRING", mode="REQUIRED"
                    )
                )
            schema.append(
                bigquery.SchemaField("etl_updatetime", "TIMESTAMP", mode="REQUIRED")
            )
            schema.append(
                bigquery.SchemaField("etl_updatemode", "STRING", mode="REQUIRED")
            )
        return schema

    def add_etl_columns_to_schema(self, schema):
        schema.append(
            bigquery.SchemaField(
                "source_file", "STRING", mode="REQUIRED", description="Source file name"
            )
        )
        schema.append(
            bigquery.SchemaField(
                "ingested_at",
                "TIMESTAMP",
                mode="REQUIRED",
                description="Ingestion timestamp",
            )
        )
        return schema

    def add_etl_to_data(
        self, df: pd.DataFrame, add_etl_src_file=False, etl_filename=None
    ):
        now_th = datetime.now(timezone("Asia/Bangkok"))
        df["etl_updatetime"] = now_th
        df["etl_updatemode"] = "insert"
        if add_etl_src_file:
            if etl_filename is None:
                raise ValueError(
                    f"Please provide the input filename when set add_etl_src_file=True"
                )
            df["etl_sourcefilename"] = etl_filename
        return df

    def delete_bq_table(self, dataset_id, table_id):
        """
        Remove the target table from your dataset
        """
        full_qualified_id = self.__get_full_qualified_table_name(dataset_id, table_id)
        try:
            self.client.delete_table(full_qualified_id, not_found_ok=True)
        except Exception as e:
            print(f"Failed to delete the table {full_qualified_id} with error {e}")
        else:
            print(f"Deleted table: {full_qualified_id}")

    def fix_none_null_value(self, df):
        df = df.where(pd.notnull(df), None)
        return df

    def get_mode_bq(self, mode):
        if mode in ("append", "incremental"):
            return "WRITE_APPEND"
        elif mode in ("truncate", "initial"):
            return "WRITE_TRUNCATE"
        else:
            raise ValueError(f"Invalid mode for inserting data to BigQuery: {mode}")

    def insert_row(self, rows, dataset_id, table_name):
        full_qualified_id = self.__get_full_qualified_table_name(dataset_id, table_name)
        table = self.client.get_table(full_qualified_id)
        errors = self.client.insert_rows(table, rows)
        if errors:
            print(f"failed to insert the input row: {errors}")

    def __update_instance(self, dataset_id, table_id):
        self.dataset_id = dataset_id
        self.table_name = table_id
        self.job_uuid = str(uuid.uuid4())

    def log2bq(self, message="no input message", is_error=0):
        if self.job_uuid is None:
            self.__update_instance(dataset_id="no_dataset_id", table_id="no_table_name")
        value = {
            "hostname": platform.uname().node,
            "job_uuid": self.job_uuid,
            "dataset_name": self.dataset_id,
            "table_name": self.table_name,
            "message": message,
            "is_error": is_error,
            "create_timestamp": datetime.now(),
        }
        value = [value]
        self.insert_row(value, self.__log_dataset, self.__log_table)

    def insert_dataframe_to_bq_table(
        self, df, dataset_id, table_id, schema, mode, update_instance=True
    ):
        """
        Insert the whole dataframe into BigQuery with proper schema

        mode['append','truncate']
        'append' = append data to the table
        'truncate' = remove all data from the table and write
        """
        # update value to the instace
        if update_instance:
            self.__update_instance(dataset_id, table_id)
        # ensure the data is good for bigquery
        df = self.fix_none_null_value(df)
        mode_bq = self.get_mode_bq(mode)
        full_qualified_id = self.__get_full_qualified_table_name(dataset_id, table_id)
        # self.log2bq(message="loading data from input dataframe to the target table")
        try:
            job_config = bigquery.LoadJobConfig(
                schema=schema, write_disposition=mode_bq
            )
            print(f"Inserting data to the table {full_qualified_id}")
            job = self.client.load_table_from_dataframe(
                df, full_qualified_id, job_config=job_config
            )
            job.result()
        except Exception as e:
            raise ValueError(f"ERROR: {e}") from e
        else:
            print(f"successfully insert data to {full_qualified_id}")
            # self.log2bq(message=f"successfully insert data to {full_qualified_id}")
            return True

    def insert_simple(self, df: pd.DataFrame, table_id: str):
        # this method BigQuery will guess the column data type by itself
        cols = [self.get_valid_colname(c) for c in df.columns]
        df.columns = cols
        job = self.client.load_table_from_dataframe(df, table_id)
        job.result()

    def prepare_sql_query(self, sql, schema_name_src, table_name_src):
        if sql is None:
            sql = f"SELECT * FROM {schema_name_src}.{table_name_src}"
        print("Using the SQL command below")
        print(sql)
        return sql

    def clean_thai_phone(self, df: pd.DataFrame, col_phone):
        df.reset_index(drop=True, inplace=True)
        if col_phone:
            for c in col_phone:
                val = df[c].apply(format_phone).to_list()
                val = pd.DataFrame(val, columns=["phone_type", "phone_number"])
                df.loc[:, c] = val["phone_number"]
        return df

    def __getcsize(self, num):
        if num is None:
            return 100000
        else:
            return num

    # def load_table_from_db(
    #     self,
    #     schema_name_src,
    #     table_name_src,
    #     dataset_id,
    #     table_name,
    #     schema_dict,
    #     loading_mode,
    #     db_engine,
    #     db_hostname_or_ip,
    #     db_port_number,
    #     db_database_name,
    #     db_username,
    #     db_password,
    #     sql=None,
    #     add_etl_cols=False,
    #     rename_dict=None,
    #     col_phone=None,
    #     csize=None,
    # ):
    #     self.__update_instance(dataset_id, table_name)
    #     self.db = self.__get_db_connection(
    #         db_hostname_or_ip,
    #         db_port_number,
    #         db_database_name,
    #         db_username,
    #         db_password,
    #         engine=db_engine,
    #     )
    #     if loading_mode.lower() == "truncate":
    #         self.clear_table(dataset_id, table_name)
    #     sql = self.prepare_sql_query(sql, schema_name_src, table_name_src)
    #     self.log2bq(message="making a request to the target database")
    #     self.log2bq(message=sql)
    #     schema = self.generate_bq_schema_from_dict(
    #         schema_dict, add_etl_cols=add_etl_cols, add_etl_filename=False
    #     )
    #     dbcsize = self.__getcsize(csize)
    #     chunk_count = 0
    #     for df in pd.read_sql(sql, self.db, chunksize=dbcsize):  # type: ignore
    #         df = self.remove_nulls(df)
    #         msg = f"found records of requested data: {df.shape[0]} for the chunk [{chunk_count}]"
    #         print(msg)
    #         self.log2bq(message=msg)
    #         if add_etl_cols:
    #             df["etl_updatetime"] = datetime.now()
    #             df["etl_updatemode"] = "INSERT"
    #             msg = f"added `etl_updatetime`, `etl_updatemode` to df"
    #             self.log2bq(message=msg)
    #         df = self.rename_columns(df, rename_col=rename_dict)
    #         dtype_config = self.generate_dtype_from_schema(schema_dict)
    #         df = self.clean_thai_phone(df, col_phone)
    #         df = self.convert_dtype(df, dtype_config)
    #         self.insert_dataframe_to_bq_table(
    #             df,
    #             dataset_id,
    #             table_name,
    #             schema,
    #             mode="append",
    #             update_instance=False,
    #         )
    #         chunk_count += 1

    def remove_nulls(self, df):
        df.fillna(np.nan, inplace=True)
        return df

    def load_table_from_postgres(
        self,
        schema_name_src,
        table_name_src,
        dataset_id,
        table_name,
        schema,
        loading_mode,
        db_hostname_or_ip,
        db_port_number,
        db_database_name,
        db_username,
        db_password,
        sql=None,
        add_etl_cols=False,
    ):
        self.__update_instance(dataset_id, table_name)
        self.db = self.__get_db_connection(
            db_hostname_or_ip,
            db_port_number,
            db_database_name,
            db_username,
            db_password,
            engine="postgres",
        )
        if sql is None:
            sql = f"SELECT * FROM {schema_name_src}.{table_name_src}"
        # self.log2bq(message="making a request to the target database")
        # self.log2bq(message=sql)
        df = pd.read_sql(sql, self.db)  # type: ignore
        print(f"found records of requested data: {df.shape[0]}")
        # self.log2bq(message=f"found records of requested data: {df.shape[0]}")
        if add_etl_cols:
            df["etl_updatetime"] = datetime.now()
            df["etl_updatemode"] = "INSERT"
            # self.log2bq(message=f"added 2 etl_updatetime, etl_updatemode to the data")
        print(df.head())
        self.insert_dataframe_to_bq_table(
            df,
            dataset_id,
            table_name,
            schema,
            loading_mode,
            update_instance=False,
        )

    def rename_columns(self, df: pd.DataFrame, rename_dict: dict):
        if rename_dict:
            return df.rename(columns=rename_dict)
        return df

    def get_schema_dict_from_db(self, df: pd.DataFrame, db_engine=None) -> dict:
        """Generate a schema dictionary from a dataframe
        https://cloud.google.com/static/architecture/dw2bq/oracle/oracle-bq-sql-translation-reference.pdf

        Args:
            df (pd.DataFrame): the input information schema dataframe

        Returns:
            dict: a dictionary of schema

        Example:
        {
            'column_name': {
                'data_type': 'STRING',
                'precision': 0,
                'scale': 0,
                'is_nullable': 'YES',
                'col_id': 1
            },
            'column_name2': {
                'data_type': 'STRING',
                'precision': 0,
                'scale': 0,
                'is_nullable': 'YES',
                'col_id': 1
            }
        }
        """
        if db_engine is None:
            raise ValueError(
                "db_engine is required to select the right data type mapping"
            )
        res = None
        if db_engine.lower() == "oracle":
            res = self.convert_oracle_dict(df)
        else:
            raise ValueError(f"db_engine {db_engine} is not supported yet")
        return res

    def convert_oracle_dict(
        self,
        df,
    ):
        res = {}
        for i, r in df.iterrows():
            gbq_col_name = self.get_valid_colname(r["COLUMN_NAME"])
            res[gbq_col_name] = {
                "data_type": self.get_gbq_type_from_oracle_type(
                    r["DATA_TYPE"], r["DATA_PRECISION"], r["DATA_SCALE"]
                ),
                "precision": r["DATA_PRECISION"],
                "scale": r["DATA_SCALE"],
                "length": r["DATA_LENGTH"],
                "is_nullable": r["NULLABLE"],
                "col_id": r["COLUMN_ID"],
            }
        return res

    def get_str_schema_from_list(self, columns, output_filename=None) -> dict:
        res = {}
        for col in columns:
            res[col] = {
                "data_type": "STRING",
                "precision": 0,
                "scale": 0,
                "length": 0,
                "is_nullable": "YES",
                "col_id": 0,
            }
        if output_filename:
            with open(output_filename, "w", encoding="utf-8") as json_file:
                json.dump(res, json_file, indent=4, ensure_ascii=False)
        return res

    def get_gbq_type_from_oracle_type(
        self, data_type: str, precision: int, scale: int
    ) -> str:
        if data_type.lower() in ("numeric", "decimal", "number"):
            data_type = self.choose_num_bignum(precision, scale)
        elif "timestamp(" in data_type.lower():
            return "TIMESTAMP"
        else:
            data_type = oracle_to_gbq.get(data_type)  # type: ignore
        if data_type is None:
            raise ValueError(f"cannot find the mapping for {data_type}")
        return data_type

    # def load_table_from_s3(
    #     self,
    #     access_key,
    #     secret_key,
    #     bucket_name,
    #     dataset_id,
    #     table_name,
    #     schema_dict,
    #     s3_prefix,
    #     loading_mode,
    #     add_etl_cols,
    #     add_etl_filename,
    #     lower_colname=True,
    #     rename_col=None,
    # ):
    #     self.__update_instance(dataset_id, table_name)
    #     schema = self.generate_bq_schema_from_dict(
    #         schema_dict,
    #         add_etl_cols=add_etl_cols,
    #         add_etl_filename=add_etl_filename,
    #     )
    #     self.create_bq_dataset(dataset_id)
    #     self.create_bq_table(dataset_id, table_id=table_name, schema=schema)
    #     self.s3 = self.get_s3_object(access_key, secret_key, bucket_name)  # type: ignore
    #     s3_files = self.s3.list_file(s3_prefix)
    #     for s3_file in s3_files:
    #         df = self.read_data_from_s3(s3_filepath=s3_file)
    #         df = self.rename_columns(df, lower_colname, rename_col)
    #         df = self.manage_etl_columns(
    #             df, s3_file, add_etl_cols, add_etl_filename
    #         )
    #         dtype_config = self.generate_dtype_from_schema(schema_dict)
    #         df = self.convert_dtype(df, dtype_config)
    #         self.insert_dataframe_to_bq_table(
    #             df,
    #             dataset_id,
    #             table_name,
    #             schema,
    #             loading_mode,
    #             update_instance=False,
    #         )

    def manage_etl_columns(
        self, df, s3_file=None, add_etl_cols=True, add_etl_filename=False
    ):
        if add_etl_cols:
            if add_etl_filename:
                if s3_file is not None:
                    df["etl_sourcefilename"] = s3_file
                else:
                    raise ValueError(f"There is no input filename")
            df["etl_updatetime"] = datetime.now()
            df["etl_updatemode"] = "INSERT"
        return df

    # def generate_dtype_from_schema(self, schema_dict):
    #     config = {
    #         "col_str": [],
    #         "col_bool": [],
    #         "col_ts": [],
    #         "col_dt": [],
    #         "col_int": [],
    #         "col_decimal": [],
    #         "col_float": [],
    #         "col_time": [],
    #     }
    #     for k, v in schema_dict.items():
    #         if v["data_type"] in ["STRING"]:
    #             config["col_str"].append(k)
    #         elif v["data_type"] in ["DATE"]:
    #             config["col_dt"].append(k)
    #         elif v["data_type"] in ["TIMESTAMP"]:
    #             config["col_ts"].append(k)
    #         elif v["data_type"] in ["INTEGER", "INT64"]:
    #             config["col_int"].append(k)
    #         elif v["data_type"] in ["NUMERIC", "DECIMAL"]:
    #             config["col_decimal"].append(self.choose_num_bignum(v))
    #         elif v["data_type"] in ["BOOLEAN", "BOOL"]:
    #             config["col_bool"].append(k)
    #         elif v["data_type"] in ["FLOAT64", "FLOAT"]:
    #             config["col_float"].append(k)
    #         elif v["data_type"] in ["TIME"]:
    #             config["col_time"].append(k)
    #         else:
    #             raise NotImplementedError(
    #                 f"the value [{v}] is not implemented yet"
    #             )
    #     return config

    def choose_num_bignum(self, precision, scale):
        if (scale is None) and (precision is None):
            return "NUMERIC"
        if scale <= 9 and precision <= 38:
            return "NUMERIC"
        else:
            return "BIGNUMERIC"

    def convert_time(self, val):
        if pd.isna(val):
            return None
        else:
            return val

    def get_row_counts(self, table_id: str):
        table = self.client.get_table(table_id)
        return table.num_rows

    def list_tables(self, dataset_name: str = "DATASET_ABC"):
        tables = []
        for table in self.client.list_tables(dataset_name):
            tables.append(table.full_table_id.replace(":", "."))
        return tables

    def list_datasets(self) -> List[bigquery.Dataset]:
        datasets = list(self.client.list_datasets())  # Make an API request.
        return datasets

    def convert_dtype(self, df: pd.DataFrame, schema_bq: List[bigquery.SchemaField]):
        for sch in schema_bq:
            print(f"Converting: {sch.name}")
            data_type = sch.field_type
            if data_type in ("NUMERIC", "BIGNUMERIC"):
                df[sch.name] = df[sch.name].apply(self.convert_to_decimal)  # type: ignore it can handle None
                # context = decimal.Context(prec=7)
                # df[col.name] = df[col.name].apply(context.create_decimal_from_float)
            elif data_type in ("TIMESTAMP", "DATETIME"):
                df[sch.name] = pd.to_datetime(df[sch.name], errors="coerce")
            elif data_type in ("DATE"):
                df[sch.name] = pd.to_datetime(df[sch.name], errors="coerce").dt.date
            elif data_type in ("TIME"):
                df[sch.name] = df[sch.name].apply(self.convert_time)  # type: ignore it can handle None
            elif data_type in ("STRING"):
                df[sch.name] = df[sch.name].astype(str)
            elif data_type in ("INTEGER"):
                df[sch.name] = df[sch.name].astype("float")
                df[sch.name] = df[sch.name].astype("Int64")
            elif data_type in ("FLOAT"):
                df = self.convert_float_cols(df, sch.name)
            elif data_type in ("BOOLEAN"):
                df = self.convert_boolean_cols(df, sch.name)
            else:
                raise NotImplementedError(
                    f"the value [{data_type}] is not implemented yet"
                )
        df.replace({"nan": None, "NaN": None}, inplace=True)
        df.replace({pd.NaT: None}, inplace=True)  # type: ignore
        return df

    def run_store_procedure(self, sql):
        # trick is add `select` statement at the end
        sql = """
        DECLARE full_refresh BOOL DEFAULT True;
        DECLARE date_ DATE DEFAULT NULL;
        CALL `cto-cds-datamart-hub-dev.ECOM_DATA_MODEL.SP_DP_ORDER`(full_refresh, date_);
        select full_refresh;
        """
        query_job = self.client.query(sql)
        rows = list(query_job.result())
        print(rows)

    def convert_to_decimal(self, val):
        """This is updated method to solve the issue of converting to decimal
        previously I use the method below, but it will cause the precision issue
        df[c] = df[c].astype(str).map(decimal.Decimal)

        Args:
            val (Any): the input value from table

        Returns:
            Decimal: Decimal value to pass into bigquery
        """
        if pd.isna(val):
            return None
        if isinstance(val, float):
            return decimal.Decimal(str(val))
        else:
            return decimal.Decimal(val)

    def convert_boolean_cols(self, df, col):
        try:
            df[col] = df[col].astype(int)
        except Exception as e:
            pass
        df[col] = df[col].astype("bool")
        return df

    def convert_float_cols(self, df, col):
        try:
            df[col] = df[col].astype(float)
        except Exception as e:
            pass
        return df

    # def read_data_from_s3(self, s3_filepath):
    #     _temp_file_path = f"./{uuid.uuid4().hex}.tempfile"
    #     self.s3.download_file(s3_filepath, _temp_file_path)
    #     if s3_filepath.endswith(".csv"):
    #         df = pd.read_csv(_temp_file_path, dtype=str)
    #     elif s3_filepath.endswith(".xlsx"):
    #         df = pd.read_excel(_temp_file_path, dtype=str, engine="openpyxl")
    #     else:
    #         raise NotImplementedError(
    #             f"the input file is not supported yet: {s3_filepath}"
    #         )
    #     os.remove(_temp_file_path)
    #     print(f"data size {df.shape}")
    #     return df

    def run_sql(self, sql: str, dry_run=False):
        if dry_run:
            job_config = bigquery.QueryJobConfig(dry_run=True, use_query_cache=False)
            query_job = self.client.query(sql, job_config=job_config)
        else:
            query_job = self.client.query(sql)
        results = query_job.result()
        return results

    def clear_table(self, dataset_id, table_id):
        """remove all records from the table, the target table must exists to run this

        Args:
                dataset_id (str): schema_name/dataset_id
                table_id (str): table_name/table_id
        """
        full_qualified_id = self.__get_full_qualified_table_name(dataset_id, table_id)
        sql = f"TRUNCATE TABLE {full_qualified_id}"
        self.run_sql(sql)

    def get_schema_from_existing_table(self, dataset_id, table_id):
        full_qualified_id = self.__get_full_qualified_table_name(dataset_id, table_id)
        table = self.client.get_table(full_qualified_id)
        return table.schema

    def generate_merge_on_key(self, col_key):
        txt = ""
        for col in col_key:
            _t = f"t.{col} = s.{col}"
            if col != col_key[-1]:
                _t = f"{_t} AND "
            txt += _t
        return txt

    def generate_sql_merge_update_set(self, columns, col_key):
        columns = [c for c in columns if c.lower() not in col_key]
        n_col = len(columns)
        txt = ""
        for index, col in enumerate(columns):
            if col == "update_mode":
                txt += f"t.{col} = 'UPDATE',\n"
            elif not (index + 1) == n_col:
                txt += f"t.{col} = s.{col},\n"
            else:
                txt += f"t.{col} = s.{col}\n"
        return txt

    def generate_sql_merge_insert_set(self, columns):
        col_txt = ",".join(columns)
        col_txt_value = ""
        for col in columns:
            col_txt_value += f"s.{col},"
        col_txt_value = col_txt_value[:-1]
        # final text to output
        txt_final = f"""
		INSERT({col_txt})
		VALUES({col_txt_value})
		"""
        return txt_final

    def create_external_table_gsheet(
        self,
        target_table_id: str = "nplearn_project.dataset.table_name",
        sheet_url: str = "https://docs.google.com/spreadsheets/d/1MOGVhsdkaZ6663xkkrRYaxN5JeJJh0J3t9acIWcidNs",
        skip_leading_rows: int = 1,
        sheet_range: str = "us-states!A20:B49",
        schema: Union[List[bigquery.SchemaField], None] = None,
    ):
        # connection id not support for this type
        table = bigquery.Table(table_ref=target_table_id, schema=schema)
        external_config = bigquery.ExternalConfig("GOOGLE_SHEETS")
        # Use a shareable link or grant viewing access to the email address you
        # used to authenticate with BigQuery (this example Sheet is public).
        # range is the sheet_name or sheet_name with cell range
        external_config.source_uris = [sheet_url]
        if skip_leading_rows:
            external_config.options.skip_leading_rows = skip_leading_rows  # type: ignore
        external_config.options.range = sheet_range  # type: ignore
        table.external_data_configuration = external_config
        # Create a permanent table linked to the Sheets file.
        table = self.client.create_table(table)  # Make an API request.

    def create_external_table_from_gcs(
        self,
        table_id: str,
        gcs_uri: str,
        file_type: str,
        connection_id: Union[str, None] = None,
        is_hive_partition: bool = False,
        schema: Union[List[bigquery.SchemaField], None] = None,
    ) -> "bigquery.Table":  # type: ignore
        # table_id = "your-project.your_dataset.your_table_name"
        # gcs_uri = "gs://cto-ris-cds-prd_converted/test/cds/jda/outbound/JDASKU/*"
        # source_uri_prefix = "gs://cto-ris-cds-prd_converted/test/cds/jda/outbound/JDASKU/"
        # Example usage: gbq.create_external_table_from_gcs(table_id=table_id,schema=None,gcs_uri=gcs_uri,avro_or_parquet='AVRO',is_hive_partition=True)
        # ================================= Choose file format =================================
        if file_type.upper() == "AVRO":
            external_config = bigquery.ExternalConfig("AVRO")
        elif file_type.upper() == "PARQUET":
            external_config = bigquery.ExternalConfig("PARQUET")
        elif file_type.upper() == "NEWLINE_DELIMITED_JSON":
            external_config = bigquery.ExternalConfig("NEWLINE_DELIMITED_JSON")
        else:
            raise NotImplementedError(f"The {file_type} type is not supported yet")
        external_config.source_uris = [gcs_uri]
        if connection_id:
            external_config.connection_id = connection_id
        source_uri_prefix = gcs_uri[:-1]
        # ================================= Set Hive partition config =================================
        if is_hive_partition:
            hive_partitioning_opts = bigquery.HivePartitioningOptions()
            hive_partitioning_opts.mode = "AUTO"
            hive_partitioning_opts.require_partition_filter = False
            hive_partitioning_opts.source_uri_prefix = source_uri_prefix
            external_config.hive_partitioning = hive_partitioning_opts
        # ================================= Set external table config =================================
        if schema is None:
            external_config.autodetect = True
            table = bigquery.Table(table_id)
        else:
            table = bigquery.Table(table_id, schema=schema)
        table.external_data_configuration = external_config
        # ================================= Create table =================================
        try:
            table = self.client.create_table(table)  # Make an API request.
        except Exception as e:
            if "Already Exists: Table" in e.args[0]:
                print(f"Table already exists: {table_id}")
            else:
                raise ValueError(e) from e
        else:
            return table

    def get_schema_policy_tag(
        self,
        col_name,
        col_type,
        col_mode,
        policy_tag_id: Union[str, None] = None,
        fields: Union[List[bigquery.SchemaField], None] = None,
        desc: str = "No description",
    ):
        """Add policy tag to the BigQuery table schema
        Args:
            col_name (tr): the name of the column
            col_type (str): the type of the column, e.g. STRING, INTEGER, FLOAT, etc.
            col_mode (str): the mode of the column, e.g. NULLABLE, REQUIRED, REPEATED
            policy_tag_id (str, optional): The policy tag full id. Defaults to None. example: projects/myproject/locations/asia-southeast1/taxonomies/11111111111111111111/policyTags/22222222222222222
        Returns:
            bigquery.SchemaField: the schema field with policy tag or without it
        """
        bq_policy = bigquery.PolicyTagList(names=[policy_tag_id])  # type: ignore
        if fields is None:
            fields = []
        if policy_tag_id:
            return bigquery.SchemaField(
                name=col_name,
                field_type=col_type,
                mode=col_mode,
                description=desc,
                fields=fields,
                policy_tags=bq_policy,
            )
        else:
            return bigquery.SchemaField(
                name=col_name,
                field_type=col_type,
                mode=col_mode,
                description=desc,
                fields=fields,
            )

    def create_external_table_from_google_sheets(
        self,
        table_id: str,
        ext_config: Union[bigquery.ExternalConfig, None] = None,
        uri: str = "",
        schema: Union[List[bigquery.SchemaField], None] = None,
    ) -> None:
        table = bigquery.Table(table_id, schema=schema)
        if ext_config:
            table.external_data_configuration = ext_config
        else:
            external_cfg = bigquery.ExternalConfig("GOOGLE_SHEETS")
            external_cfg.source_uris = [uri]
            external_cfg.options.skip_leading_rows = 1  # type: ignore
            # external_cfg.autodetect = True
            # external_cfg.max_bad_records = 2
            external_cfg.ignore_unknown_values = False
            table.external_data_configuration = external_cfg
        table = self.client.create_table(table)
        print(table)

    # ================================= Get data from GBQ =================================
    def get_data_from_gbq(self, sql: str) -> pd.DataFrame:
        # sql = "SELECT * FROM `bigquery-public-data.irs_990.irs_990_2012`"
        # need package: google-cloud-bigquery-storage, pyarrow
        return self.client.query(sql).to_dataframe()

    def get_data_from_gbq_2(self, sql: str) -> pd.DataFrame:
        return (
            self.client.query(sql)
            .result()
            .to_dataframe(
                bqstorage_client=bqstorageclient,
                progress_bar_type="tqdm",
            )
        )

    # ================================= Schedule query =================================
    # original note: https://github.com/noppGithub/google-gcloud-cli/blob/main/bq.sh
    def list_configs(self, project_id: str, location: str, simplify=False):
        parent = f"projects/{project_id}/locations/{location}"
        configs = self.client_sq.list_transfer_configs(parent=parent)
        if simplify:
            return self.simplify_transfer_config(configs)
        return configs

    def simplify_transfer_config(self, configs):
        data = []
        for config in configs:
            data.append(
                {
                    "name": config.name,
                    "display_name": config.display_name,
                    "datasource_id": config.data_source_id,
                    "state": config.state,
                    "schedule": config.schedule,
                    "destination_dateset_id": config.destination_dataset_id,
                    "dataset_region": config.dataset_region,
                    "query": config.params.get("query"),  # type: ignore
                }
            )
        return data

    def transferconfig_disable(self, tc: bigquery_datatransfer.TransferConfig):
        tc.disabled = True  # type: ignore
        request = bigquery_datatransfer.UpdateTransferConfigRequest(
            transfer_config=tc,
            update_mask=FieldMask(paths=["disabled"]),
            # add more fields to the list when you make changes, this case only has 1 change
        )
        response = self.client_sq.update_transfer_config(request=request)

    def transferconfig_delete(self, name: str):
        self.client_sq.delete_transfer_config(name=name)

    def transferconfig_get(self, transfer_name: str):
        client = bigquery_datatransfer_v1.DataTransferServiceClient()
        request = bigquery_datatransfer_v1.GetTransferConfigRequest(
            name=transfer_name,
        )
        response = client.get_transfer_config(request=request)
        return response

    def transferconfig_get_v1(self, transfer_name: str):
        client = bigquery_datatransfer.DataTransferServiceClient()
        request = bigquery_datatransfer.GetTransferConfigRequest(
            name=transfer_name,
        )
        response = client.get_transfer_config(request=request)
        return response

    def transferconfig_add_labels(self, sql: str, labels: Union[dict, None]):
        """
        Adding the labels to the query, since the GCP scheduled query does not support labels
        We have to add it to the SQL body
        This will allow us to make query to check the query with the labels below
        ===========================================================================================
        SELECT creation_time, job_id, parent_job_id, user_email, labels, query, total_bytes_billed
        FROM `cto-cds-datamart-hub-prod`.`region-asia-southeast1`.INFORMATION_SCHEMA.JOBS
        WHERE creation_time >= '2023-10-18'
        and query like '%drv_brand_day_target%'
        ORDER BY creation_time DESC
        """
        if labels:
            label_txt = ""
            for k, v in labels.items():
                label_txt += f'SET @@query_label = "{k}:{v}";\n'
            return f"{label_txt}{sql}\n"
        return sql

    def transferconfig_create(
        self,
        project_id: str,
        location: str,
        sql: str,
        dataset_id: str,
        display_name: str,
        service_account_name: str,
        schedule: str = "every 4 hours synchronized",
        labels: Union[dict, None] = None,
    ):
        # https://cloud.google.com/bigquery/docs/scheduling-queries#python_1
        # parent = self.client_sq.common_project_path(project_id)
        sql = self.transferconfig_add_labels(sql, labels)
        parent = f"projects/{project_id}/locations/{location}"
        transfer_config = bigquery_datatransfer.TransferConfig(
            # can ignore destination_dataset
            # destination_dataset_id=dataset_id,
            display_name=display_name,
            data_source_id="scheduled_query",
            params={
                "query": sql,
                # "destination_table_name_template": "demo_destination_table",
                # "overwrite_destination_table": True,
                # "destination_table_name_template": "",
                # "write_disposition": "WRITE_TRUNCATE",
                # "partitioning_field": "",
            },
            schedule=schedule,
            schedule_options=bigquery_datatransfer.ScheduleOptions(
                start_time=datetime.now(timezone("UTC"))
            ),
        )
        transfer_config = self.client_sq.create_transfer_config(
            bigquery_datatransfer.CreateTransferConfigRequest(
                parent=parent,
                transfer_config=transfer_config,
                service_account_name=service_account_name,
            )
        )
        print(
            f"Created schedule query {transfer_config.display_name} with id={transfer_config.name}"
        )

    def transfer_config_update_sa(
        self,
        transfer_name,
        service_account_email="npsample@myproject.iam.gserviceaccount.com",
    ):
        # 2023-12-02 21:34: Tested pas
        # https://github.com/GoogleCloudPlatform/python-docs-samples/blob/HEAD/bigquery-datatransfer/snippets/manage_transfer_configs.py
        tc = self.transferconfig_get(transfer_name)
        tc_client = bigquery_datatransfer.DataTransferServiceClient()
        new_config = bigquery_datatransfer.TransferConfig(name=transfer_name)
        new_config.display_name = tc.display_name
        new_config = tc_client.update_transfer_config(
            {
                "transfer_config": new_config,
                "update_mask": FieldMask(paths=["service_account_name"]),
                "service_account_name": service_account_email,
            }
        )
        print(f"Updated the config:{transfer_name} to use {service_account_email}")

    def transfer_config_update(
        self, sql_new: str = "", transfer_name: str = "", schedule: str = ""
    ):
        # transfer_name is the same as resource_name in the UI
        # projects/802813315299/locations/asia-southeast1/transferConfigs/651409f4-0000-24b3-b306-f403045ed092
        tc = self.transferconfig_get(transfer_name)
        transfer_client = bigquery_datatransfer.DataTransferServiceClient()
        new_params = {
            "query": sql_new,
            # "destination_table_name_template": "your_table_{run_date}",
            # "write_disposition": "WRITE_TRUNCATE",
            # "partitioning_field": "",
        }
        transfer_config = bigquery_datatransfer.TransferConfig(name=transfer_name)
        transfer_config.display_name = tc.display_name
        transfer_config.params = new_params  # type: ignore
        if schedule:
            transfer_config.schedule = schedule
        transfer_config = transfer_client.update_transfer_config(
            transfer_config=transfer_config,
            update_mask=FieldMask(paths=["display_name", "params"]),
        )
        print(f"Updated config: {transfer_config.display_name}")

    def delete_config(self, name: str):
        try:
            self.client_sq.delete_transfer_config(name=name)
        except Exception as e:
            print("Transfer config not found.")
        else:
            print(f"Deleted transfer config: {name}")

    def remove_all_policy_tag(self, table_id: str):
        new_schema = []
        tbl = self.client.get_table(table_id)
        for field in tbl.schema:
            new_schema.append(self.get_field_no_policy_tag(field))
        tbl.schema = new_schema
        self.client.update_table(tbl, ["schema"])

    def copy_table(self, tbl_id_src, tbl_id_dst):
        job = self.client.copy_table(tbl_id_src, tbl_id_dst)
        result = job.result()
        print(f"Copy table result:{result.state}")

    def wait_table_exist(self, table_id):
        is_exists = False
        while not is_exists:
            try:
                tbl = self.client.get_table(table_id)
            except Exception as e:
                print(f"Table not exists yet...{e}")
                sleep(1)
            else:
                is_exists = True

    def get_field_no_policy_tag(self, field):
        if len(field.fields) == 0:
            return bigquery.SchemaField(
                name=field.name,
                field_type=field.field_type,
                mode=field.mode,
                description=field.description,
                policy_tags=bigquery.PolicyTagList(names=[]),
            )
        fields_out = []
        for f in field.fields:
            fields_out.append(self.get_field_no_policy_tag(f))
        return bigquery.SchemaField(
            name=field.name,
            field_type=field.field_type,
            mode=field.mode,
            description=field.description,
            fields=fields_out,
        )

    def is_nested(self, field):
        if len(field.fields) == 0:
            return False
        return True

    def get_field_detail(self, field):
        if not self.is_nested(field):
            return {
                "name": field.name,
                "field_type": field.field_type,
                "mode": field.mode,
                "description": field.description,
                "policy_tags": self.get_field_policy_tag(field),
            }
        fields_out = []
        for f in field.fields:
            fields_out.append(self.get_field_detail(f))
        return {
            "name": field.name,
            "field_type": field.field_type,
            "mode": field.mode,
            "description": field.description,
            "policy_tags": self.get_field_policy_tag(field),
            "fields": fields_out,
        }

    def get_field_policy_tag(self, field):
        if field.policy_tags:
            # return the first one, since Google document said that only 1 tag for a column
            return field.policy_tags.names[0]
        return None

    def extract_table_schema(
        self, table_id="your-project.your_dataset.your_table_name", include_nested=True
    ):
        table = self.client.get_table(table_id)
        output = []
        for field in table.schema:
            field_detail = self.get_field_detail(field)
            if include_nested:
                output.append(field_detail)
            else:
                if "fields" in field_detail:
                    field_detail.pop("fields")
                    output.append(field_detail)
                else:
                    output.append(field_detail)
        return output
