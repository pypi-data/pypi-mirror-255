import datetime
import logging
import math
import os
import re
from logging.handlers import RotatingFileHandler
from pathlib import Path
from time import sleep

import pandas as pd
import pyodbc
import sqlalchemy
from pytz import timezone

# Log settings
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s:%(levelname)s:%(name)s:%(message)s")
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)


class NPMSSql(object):
    def __init__(
        self,
        hostname_or_ip,
        database_name,
        username,
        password,
        protocal="tcp",
        port_number=1433,
        instance_id=1,
    ):
        """A helper class to work with Microsoft SQL server
        It is designed to work with the Pandas dataframe as well

        Default protocal is TCP with port 1433
        """
        # Versioning
        self.__classname__ = "NPMSSql"
        self.__author__ = "n.phantawee@gmail.com"
        self.__version__ = 1.00
        self.__changelog__ = {"1.00": "Merge all valid method into a class"}
        # Log file settings
        log_dir = "./log"
        log_filename = f"{self.__classname__}_{instance_id:02d}.log"
        self.__create_log_dir(log_dir)
        self.__create_log_file(log_dir=log_dir, log_filename=log_filename)
        # Class variables
        self.hostname_or_ip = hostname_or_ip
        self.hostname_alias = self.__get_hostname_alias()
        self.database_name = database_name
        self.username = username
        self.password = password
        self.protocal = str(protocal).lower()
        self.port_number = port_number
        self.driver = self.__get_odbc_driver()
        self.conn = self.__get_connection()
        # self.cursor = self.__get_cursor()
        # engine is use for working with Python sqlalchemy
        self.engine = self.__get_engine()

    def __create_log_dir(self, log_dir):
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
            logger.info(f"The log directory [{log_dir}] has been created")
        else:
            logger.warn(f"The log directory [{log_dir}] is already exist")

    def __create_log_file(self, log_dir, log_filename):
        log_path = os.path.join(log_dir, log_filename)
        # limit file size to 1 MB with one backup
        file_handler = RotatingFileHandler(
            log_path,
            mode="a",
            maxBytes=50 * 1024 * 1024,
            backupCount=1,
            encoding="utf-8",
            delay=False,
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    def __get_hostname_alias(self):
        """
        generate the nickname of hostname
        """
        hostname = re.sub("[^0-9]+", "", self.hostname_or_ip)
        if not hostname.isdigit():
            hostname = self.hostname_or_ip.split(".")[0]
        else:
            hostname = self.hostname_or_ip.replace(".", "-")
        return hostname

    # ============================================= Private methods =============================================
    def __get_odbc_driver(self):
        # old version, I have to use {'ODBC Driver 17 for SQL Server'} as the driver name
        available_drivers = pyodbc.drivers()
        logger.info(f"Available drivers:{available_drivers}")
        # ensure we have a driver
        if len(available_drivers) == 0:
            raise ValueError("There is no driver available")
        # select driver
        if "ODBC Driver 17 for SQL Server" in available_drivers:
            return "ODBC Driver 17 for SQL Server"
        elif "ODBC Driver 13 for SQL Server" in available_drivers:
            return "ODBC Driver 13 for SQL Server"
        else:
            return available_drivers[0]

    def _get_connection_string(self):
        # If using Kerberos authentication add this text to the connection string `Trusted_Connection=Yes;`
        # Sometime I add ;TrustServerCertificate=no;Connection Timeout=15;
        # Sometime I add ;TrustServerCertificate=yes;Connection Timeout=15;
        server_name = f"{self.protocal}:{self.hostname_or_ip},{self.port_number}"
        connection_string = f"DRIVER={self.driver};SERVER={server_name};DATABASE={self.database_name};UID={self.username};PWD={self.password};"
        connection_string = f"DRIVER={self.driver};SERVER={server_name};DATABASE={self.database_name};UID={self.username};PWD={self.password};TrustServerCertificate=yes;"
        return connection_string

    def __get_connection(self):
        logger.info(f"Getting connection for [{self.database_name}]")
        connection_string = self._get_connection_string()
        try:
            conn = pyodbc.connect(connection_string)
        except Exception as e:
            logger.error(f"Failed to get conn for {self.database_name} after 5 retries")
            return None
        logger.info(f"Connected to the database {self.database_name}")
        return conn

    def __get_cursor(self):
        return self.conn.cursor()  # type: ignore

    def __get_engine(self):
        # return sqlalchemy.create_engine("mssql+pyodbc://dnaadmin:Insee555@dnadbserver.database.windows.net:1433/dnadb?driver=ODBC+Driver+17+for+SQL+Server",echo=True)
        driver_name = self.driver
        # remove the { and } signs, actually we can keep it
        driver_name = driver_name.replace("{", "")
        driver_name = driver_name.replace("}", "")
        driver_name = driver_name.replace(" ", "+")
        conn_str = (
            "mssql+pyodbc://"
            + self.username
            + ":"
            + self.password
            + "@"
            + self.hostname_or_ip
            + ":1433/"
            + self.database_name
            + "?driver="
            + driver_name
        )
        engine = sqlalchemy.create_engine(conn_str, echo=True)
        # conn_str2 = f"mssql+pyodbc://{self.username}:{self.password}@{self.server_name}:{self.port_number}/{self.database_name}?driver={driver_name}"
        # engine2 = sqlalchemy.create_engine(conn_str2,echo=True)
        # result = self.__engine_check(engine)
        # result = self.__engine_check(engine2)
        return engine

    def __engine_check(self, sqlalchemy_engine_obj):
        try:
            cnx = sqlalchemy_engine_obj.connect()
        except Exception as e:
            logger.error(f"Error {e}")
            return False
        else:
            logger.info(f"SQLAlchemy engine is working")
            return True

    # ============================================= Public methods =============================================
    def get_data_from_db(self, sql):
        return pd.read_sql(sql, self.conn)  # type: ignore

    def create_table_from_df(self, df, table_name, dtype=None):
        # chunksize : int, optional ,Rows will be written in batches of this size at a time. By default, all rows will be written at once.
        # it is recommended to pass the dtype to specify your table configurations
        logger.info(
            "Creating table name {} with data size {} to database".format(
                table_name, df.shape
            )
        )
        if dtype is not None:
            logger.info("Creating table with custom dtype {}".format(dtype))
            df.to_sql(
                table_name,
                con=self.engine,
                if_exists="replace",
                index=False,
                chunksize=1000,
                dtype=dtype,
            )
        else:
            logger.info("Creating table without custom dtype")
            df.to_sql(
                table_name,
                con=self.engine,
                if_exists="replace",
                index=False,
                chunksize=1000,
            )
        logger.info(
            "Created table {} with data size {} to database".format(
                table_name, df.shape
            )
        )

    def append_table_from_df(self, df, table_name):
        logger.info("Appending data size {} to database".format(df.shape))
        df.to_sql(
            table_name, con=self.engine, if_exists="append", chunksize=1000, index=False
        )
        logger.info("Completed appending data size {} to database".format(df.shape))

    def fetch_n_rows(self, table_name, nrows=5):
        self.cursor.execute("select * from {}".format(table_name))
        for row in self.cursor.fetchall()[:nrows]:
            print(row)

    def select_data(self, sql):
        retry_flag = True
        while retry_flag == True:
            try:
                self.cursor.execute(sql)
            except Exception as e:
                self.conn = self.__get_connection()
                self.cursor = self.__get_cursor()
            else:
                rows = self.cursor.fetchall()
                retry_flag = False
        return rows

    def run_sql(self, sql, params=None):
        logger.info("Executing SQL: {}".format(sql))
        retry_flag = True
        retry_count = 0
        while (retry_flag == True) and (retry_count < 5):
            try:
                if params == None:
                    self.cursor.execute(sql)
                    logger.info("The SQL command without parameters is completed")
                else:
                    self.run_sql_with_params(sql, params)
                    logger.info(
                        "The SQL command with {} parameters is completed".format(
                            len(params)
                        )
                    )
            except Exception as e:
                logger.error("Error:{}".format(e))
                self.conn = self.__get_connection()
                self.cursor = self.__get_cursor()
                retry_count += 1
            else:
                self.conn.commit()
                logger.info("Committed to database")
                retry_flag = False

    def run_sql_with_params(self, sql, params, chunk_size=10000):
        if len(params) > 10000:
            logger.info(
                "Total input parameters is [{}] which is > 10000, splitting into chunk of 10000".format(
                    len(params)
                )
            )
            rounds = len(params) / chunk_size
            rounds = math.ceil(rounds)
            logger.info(
                "Data size [{}]/Chunk size [{}] = Rounds [{}]".format(
                    len(params), chunk_size, rounds
                )
            )
            start = 0
            end = chunk_size
            for r in range(rounds):
                logger.info("Round [{}/{}] is in progress".format(r + 1, rounds))
                self.cursor.fast_executemany = True
                self.cursor.executemany(sql, params[start:end])
                self.cursor.fast_executemany = False
                self.conn.commit()
                start += chunk_size
                end += chunk_size
                logger.info("Round [{}/{}] is completed".format(r + 1, rounds))
        else:
            logger.info(
                "Total input parameters is [{}] which is <= 10000, Loading data to the database".format(
                    len(params)
                )
            )
            self.cursor.fast_executemany = True
            self.cursor.executemany(sql, params)
            self.cursor.fast_executemany = False
            self.conn.commit()
        logger.info("Inserted {} records to the database".format(len(params)))

    def run_sql_debug(self, sql, params):
        """
        - This method will insert data to SQL table line by line to see which line values cause the error
        """
        total_params = len(params)
        for index, p in enumerate(params):
            try:
                a_list = []
                a_list.append(p)
                self.cursor.fast_executemany = True
                self.cursor.executemany(sql, a_list)
                self.cursor.fast_executemany = False
            except Exception as e:
                raise ValueError(f"Error at index [{index}] with parameter [{p}]")
            else:
                logger.info(f"{index}/{total_params} pass")
        self.conn.commit()
        logger.info("There is no error in the parameters")

    def prepare_cols_dtype(self, df, all_nvarchar=False, col_date=[]):
        """
        - The better way is still define column data type manually, since you should know suitable data type for columns
        - Check dtype of dataframe column and output dict for using with `sqlalchemy`
        - Check if there is column with length over 255
        - Any column without data type in dict will handle by `sqlalchemy` logic
        example_dict = {'my_datetime_col': sqlalchemy.DateTime(),
                        'my_date_col': sqlalchemy.Date()
                        'my_int_col':  sqlalchemy.types.INTEGER(),
                        'my_unicode_text_col': sqlalchemy.types.NVARCHAR(length=255),
                        'my_float_col': sqlalchemy.types.Float(precision=3, asdecimal=True),
                        'my_boolean_col': sqlalchemy.types.Boolean}
        """
        logger.info("Checking each column of dataframe")
        if all_nvarchar:
            return {col_name: sqlalchemy.types.NVARCHAR for col_name in df}
        else:
            my_dtype = {}
            col_names = df.columns
            col_dtypes = df.dtypes.astype("str")
            for index, (col_name, col_dtype) in enumerate(zip(col_names, col_dtypes)):
                if index in col_date:
                    my_dtype[col_name] = sqlalchemy.types.DATETIME
                    # my_dtype[col_name] = sqlalchemy.types.DATETIME
                    logger.info(
                        "Column name:{}, Column type:{}".format(col_name, "DATE")
                    )
                elif col_dtype == "object":
                    length_max = df[col_name].astype(str).str.len().max()
                    if length_max >= 5000:
                        # set to max possible with None or max keyword
                        length_data = "max"
                    else:
                        length_data = length_max + 2000
                    # set column dict
                    my_dtype[col_name] = sqlalchemy.types.NVARCHAR(length=length_data)
                    logger.info(
                        "Column name:{}, Column type:{}, Max length:{}".format(
                            col_name, col_dtype, length_data
                        )
                    )
        return my_dtype

    def convert_df_to_params(self, df):
        """
        - since `np.float64` and other type of number can show blank value as `nan`, they need to be replaced with `None` for passing through `pyodbc`
        - to solve this we use `df.where((pd.notnull(df)), None)`
        - df.replace({pd.NaT:None}) is better than df.replace(pd.NaT,None)
        """
        df = df.replace({pd.NaT: None})
        df = df.where((pd.notnull(df)), None)
        return [tuple(x) for x in df.values]

    def remove_all_rows_from_table(self, table_name):
        sql = "DELETE FROM {};".format(table_name)
        self.run_sql(sql)
        logger.info("Removed all records from table {}".format(table_name))

    def generate_n_sql_var(self, num):
        output = ""
        for i in range(num):
            if i == 0:
                output = "?"
            else:
                output = output + ",?"
        return output

    def count_query_row(self, sql_input):
        """
        - Example:
            sql = 'select * from table_namewhere MONTH([date_column]) = 7 AND YEAR([date_column]) = 2019'
            count_resultl = self.countQueryRow(sql)
        """
        sql = """select count(1) from ({})
                as result;""".format(
            sql_input
        )
        count_found = self.cursor.execute(sql).fetchone()
        return count_found[0]

    def count_table_row(self, table_name):
        sql = "select count(*) from {}".format(table_name)
        return self.cursor.execute(sql).fetchone()[0]

    def _list_to_sql_in(self, mylist, mode="text"):
        """generate ('a','b','c') from [a,b,c]
        so you can use this in the command below
        `delete from my_table where my_column in ('a','b','c')`
        """
        s = "("
        if mode == "text":
            for i in mylist:
                s = s + "'{}',".format(i)
            s = s[:-1]
            s += ")"
        else:
            # mode == number
            for i in mylist:
                s = s + "{},".format(i)
            s = s[:-1]
            s += ")"
        return s

    def _convert_cols_to_cols_sql(self, cols):
        string_long = ""
        for col in cols:
            string_long += "[{}],".format(col)
        cols_sql = string_long[:-1]
        return cols_sql

    def _get_9999_datetime(self):
        return datetime.datetime(year=9999, month=12, day=31)

    def convert_date_cols(self, df, col_dict):
        """Loop over the `key` and `value` of the input columns
        key = column index
        value = format of the input date_time like string
        """
        if (col_dict is None) or (len(col_dict) < 1):
            return df
        fix_datetime = self._get_9999_datetime()
        for col_index, date_format in col_dict.items():
            # df.iloc[:,col_index] = pd.to_datetime(df.iloc[:,col_index], format=date_format, errors='coerce')
            df.iloc[:, col_index] = pd.to_datetime(
                df.iloc[:, col_index], format=date_format, errors="coerce"
            ).dt.date.fillna(fix_datetime)
        return df

    def get_size_all_tables(self):
        sql = """SELECT 
            t.NAME AS TableName,
            s.Name AS SchemaName,
            p.rows,
            SUM(a.total_pages) * 8 AS TotalSpaceKB, 
            CAST(ROUND(((SUM(a.total_pages) * 8) / 1024.00), 2) AS NUMERIC(36, 2)) AS TotalSpaceMB,
            SUM(a.used_pages) * 8 AS UsedSpaceKB, 
            CAST(ROUND(((SUM(a.used_pages) * 8) / 1024.00), 2) AS NUMERIC(36, 2)) AS UsedSpaceMB, 
            (SUM(a.total_pages) - SUM(a.used_pages)) * 8 AS UnusedSpaceKB,
            CAST(ROUND(((SUM(a.total_pages) - SUM(a.used_pages)) * 8) / 1024.00, 2) AS NUMERIC(36, 2)) AS UnusedSpaceMB
        FROM 
            sys.tables t
        INNER JOIN      
            sys.indexes i ON t.OBJECT_ID = i.object_id
        INNER JOIN 
            sys.partitions p ON i.object_id = p.OBJECT_ID AND i.index_id = p.index_id
        INNER JOIN 
            sys.allocation_units a ON p.partition_id = a.container_id
        LEFT OUTER JOIN 
            sys.schemas s ON t.schema_id = s.schema_id
        WHERE 
            t.NAME NOT LIKE 'dt%' 
            AND t.is_ms_shipped = 0
            AND i.OBJECT_ID > 255 
        GROUP BY 
            t.Name, s.Name, p.Rows
        ORDER BY 
            TotalSpaceMB DESC, t.Name
        """
        return pd.read_sql(sql, self.conn)  # type: ignore

    def get_schema_columns(self):
        sql = """
        SELECT * 
        FROM information_schema.columns
        where table_name in (select table_name from information_schema.tables where table_type = 'BASE TABLE')
        """
        return pd.read_sql(sql, self.conn)  # type: ignore

    def list_database(self):
        sql = "SELECT name FROM master.sys.databases"
        df = pd.read_sql(sql, self.conn)  # type: ignore
        return df["name"].to_list()

    def get_tables_info(self):
        sql = """
        select *
        from information_schema.tables
        where table_schema not like 'information_schema'
        and table_type = 'BASE TABLE'
        order by table_schema,table_name 
        """
        df = pd.read_sql(sql, self.conn)
        return df

    def create_path(self, path_name):
        Path(path_name).mkdir(parents=True, exist_ok=True)

    def get_columns_info(self, table_name=None):
        if table_name is None:
            sql = """
            select *
            from information_schema.columns
            where table_schema not like 'information_schema'
            order by table_schema,table_name 
            """
        else:
            sql = f"""
            select *
            from information_schema.columns
            where table_schema not like 'information_schema'
            and table_name like '{table_name}'
            order by table_schema,table_name
            """
        df = pd.read_sql(sql, self.conn)
        df = self.rename_tbinfo_columns(df)
        return df

    def export_query(self, sql, full_path):
        path_name, file_name = os.path.split(full_path)
        self.create_path(path_name)
        try:
            with open(full_path, "w") as f:
                f.write(sql)
        except Exception as e:
            return False
        else:
            return True

    def export_df(self, df, path):
        """export the df to the selected path
        it will try 2 times, first time will just do the direct extract
        the second time will do convert those object columns to string to avoid can not infer object

        Args:
            df (dataframe): input dataframe
            path (str): path to export data

        Returns:
            bool: return True if success else False
        """
        path_name, file_name = os.path.split(path)
        self.create_path(path_name)
        max_retry = 2
        retry_flag = True
        while (retry_flag == True) and (max_retry > 0):
            try:
                df.to_parquet(
                    path, index=False, engine="fastparquet", compression="gzip"
                )
            except Exception as e:
                logger.error(f"Failed to export data: {e}")
                max_retry -= 1
                df = self.convert_all_obj_col_to_str(df)
            else:
                retry_flag = False
                return True
        # return False after those tries
        return False

    def convert_all_obj_col_to_str(self, df):
        cols = self.get_object_col_names(df)
        df[cols] = df[cols].astype(str)
        return df

    def get_object_col_names(self, df):
        """
        get the list of columns with type `object`
        """
        column_list = df.select_dtypes(include="object").columns.to_list()
        return column_list

    def export_table(
        self, schema_name, table_name, chunk_size=100000, sql=None, suffix=None
    ):
        # the user can also supply their sql command as well
        now_th = datetime.datetime.now(timezone("Asia/Bangkok"))
        nowtxt = now_th.strftime("%Y-%m-%d")
        year, month, day = nowtxt[:4], nowtxt[5:7], nowtxt[8:10]
        # export SQL
        path_sql_file = f"./output/{self.hostname_alias}/{self.database_name}/{schema_name}/{table_name}/{year}/{month}/{day}/sql/{schema_name}_{table_name}.sql"
        result = self.export_query(sql, path_sql_file)
        # export column info
        path_colinfo_file = f"./output/{self.hostname_alias}/{self.database_name}/{schema_name}/{table_name}/{year}/{month}/{day}/tbinfo/{schema_name}_{table_name}.parquet"
        df = self.get_columns_info(table_name=table_name)
        result = self.export_df(df, path_colinfo_file)
        # export data
        # query
        if sql is None:
            sql = f"SELECT * FROM [{schema_name}].[{table_name}]"
        dfs = pd.read_sql(sql, self.conn, chunksize=chunk_size)
        path_data = f"./output/{self.hostname_alias}/{self.database_name}/{schema_name}/{table_name}/{year}/{month}/{day}/data/"
        nrows_exported = 0
        for _df in dfs:
            nrows = _df.shape[0]
            to_row = nrows_exported + nrows
            if suffix is None:
                file_name = f"{table_name}_{nrows_exported:010d}-{to_row:010d}.parquet"
            else:
                file_name = (
                    f"{table_name}_{suffix}_{nrows_exported:010d}-{to_row:010d}.parquet"
                )
            full_path = os.path.join(path_data, file_name)
            ressult = self.export_df(_df, full_path)
            nrows_exported = to_row
            logger.info(f"Exported to {file_name} total {nrows_exported} rows exported")

    def rename_tbinfo_columns(self, df):
        # each database engine has different column name for INFORMATION_SCHEMA, generalize it
        df.columns = [c.lower() for c in df.columns]
        col_rename_dict = {
            # postgres
            "column_default": "default_value",
            "character_maximum_length": "max_char",
            # postgres
            "table_catalog": "database_name",
            "table_schema": "schema_name",
            "table_name": "table_name",
            "column_name": "column_name",
            "is_nullable": "is_nullable",
            "data_type": "data_type",
            # oracle
            "owner": "schema_name",
            "table_name": "table_name",
            "column_name": "column_name",
            "data_type": "data_type",
            "nullable": "is_nullable",
            # mysql
            "table_catalog": "database_name",
            "table_schema": "schema_name",
            "table_name": "table_name",
            "column_name": "column_name",
            "is_nullable": "is_nullable",
            "data_type": "data_type",
        }
        return df.rename(columns=col_rename_dict)
