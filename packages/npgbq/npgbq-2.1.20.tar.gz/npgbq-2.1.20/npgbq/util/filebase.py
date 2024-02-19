def get_sql_from_file(fp):
    with open(fp, "r", encoding="utf-8") as f:
        sql = f.read()
    return sql
