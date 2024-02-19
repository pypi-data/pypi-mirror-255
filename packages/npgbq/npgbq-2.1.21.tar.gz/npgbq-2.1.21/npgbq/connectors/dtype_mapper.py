mssql_to_gbq = {
    "bigint": "INTEGER",
    "tinyint": "INTEGER",
    "bit": "BOOL",
    "char": "STRING",
    "date": "DATE",
    "datetime": "TIMESTAMP",
    "decimal": "FLOAT",
    "int": "INTEGER",
    "money": "FLOAT",
    "smallmoney": "FLOAT",
    "nchar": "STRING",
    "numeric": "FLOAT",
    "nvarchar": "STRING",
    "real": "FLOAT",
    "smalldatetime": "TIMESTAMP",
    "smallint": "INTEGER",
    "time": "TIME",
    "varchar": "STRING",
    "float": "FLOAT",
    "varbinary": "STRING",
    "image": "STRING",
}

mysql_to_gbq = {
    "bigint": "INTEGER",
    "bit": "BOOL",
    "char": "STRING",
    "date": "DATE",
    "datetime": "TIMESTAMP",
    "decimal": "FLOAT",
    "int": "INTEGER",
    "money": "FLOAT",
    "nchar": "STRING",
    "numeric": "FLOAT",
    "nvarchar": "STRING",
    "real": "FLOAT",
    "smalldatetime": "TIMESTAMP",
    "smallint": "INTEGER",
    "time": "TIME",
    "varchar": "STRING",
    "float": "FLOAT",
}

postgres_to_gbq = {
    "bigint": "INTEGER",
    "bit": "BOOL",
    "char": "STRING",
    "date": "DATE",
    "datetime": "TIMESTAMP",
    "decimal": "FLOAT",
    "int": "INTEGER",
    "money": "FLOAT",
    "nchar": "STRING",
    "numeric": "FLOAT",
    "nvarchar": "STRING",
    "real": "FLOAT",
    "smalldatetime": "TIMESTAMP",
    "smallint": "INTEGER",
    "time": "TIME",
    "varchar": "STRING",
    "float": "FLOAT",
}


oracle_to_gbq = {
    # https://cloud.google.com/static/architecture/dw2bq/oracle/oracle-bq-sql-translation-reference.pdf
    "VARCHAR2": "STRING",
    "NVARCHAR2": "STRING",
    "CHAR": "STRING",
    "NCHAR": "STRING",
    "CLOB": "STRING",
    "NCLOB": "STRING",
    # integer
    "INTEGER": "INTEGER",
    "SHORTINTEGER": "INTEGER",
    "LONGINTEGER": "INTEGER",
    # BigQuery does not allow user specification of custom values for precision or scale. As a result, a column in Oracle might be defined so that it has a bigger scale than BigQuery supports. Additionally, before storing a decimal number, Oracle rounds up if that number has more digits after the decimal point than are specified for the corresponding column. In BigQuery, you can implement this feature by using the ROUND() function.
    "NUMBER": "NUMERIC",
    # FLOAT is an exact data type, and it’s a NUMBER subtype in Oracle. In BitQuery, FLOAT is an approximate data type. NUMERIC is often a better match for FLOAT type in BigQuery
    "FLOAT": "FLOAT",
    "BINARY_DOUBLE": "FLOAT",
    "BINARY_FLOAT": "FLOAT",
    # The LONG data type is used in earlier versions and is not suggested in new versions of Oracle Database. The BYTES data type in BigQuery can be used if it is necessary to hold LONG data in BigQuery. A better approach is putting binary objects in Cloud Storage and holding references in BigQuery.
    "LONG": "BYTES",
    # The BYTES data type can be used to store variable-length binary data. If this field is not queried and not used in analytics, a better option is to store binary data in Cloud Storage.
    "BLOB": "STRING",
    # Binary files can be stored in Cloud Storage, and the STRING data type can be used for referencing files in a BigQuery table.
    "BFILE": "STRING",
    "DATE": "DATE",
    # BigQuery supports microsecond precision (10 -6 ), in comparison to Oracle, which supports precision ranging from 0 to 9. BigQuery supports a time zone region name from a TZ database and time zone offset from UTC. In BigQuery, use a manual time zone conversion to match Oracle’s TIMESTAMP WITH LOCAL TIME ZONE feature.
    "TIMESTAMP": "TIMESTAMP",
    # The BYTES data type can be used to store variable-length binary data. If this field is not queried and used in analytics, a LONG RAW better option is to store binary data on Cloud Storage.
    "RAW": "BYTES",
    "LONG RAW": "STRING",
    # These data types are used by Oracle internally to specify unique addresses to rows in a table. Normally ROWID or UROWID fields should not be used in applications. But if this is the case, the STRING data type can be used to hold this data.
    "ROWID": "STRING",
}
