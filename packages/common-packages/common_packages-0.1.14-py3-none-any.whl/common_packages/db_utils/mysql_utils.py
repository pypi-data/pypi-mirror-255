from urllib.parse import quote_plus

import pandas as pd
from pandas import DataFrame, Series
from sqlalchemy import create_engine


class MysqlOperator:
    def __init__(self, **kwargs) -> None:
        if not {"host", "port", "user", "password", "database"}.issubset(kwargs.keys()):
            raise ValueError("host,port,user,password,database must be provided")
        self.host = kwargs["host"]
        self.port = kwargs["port"]
        self.user = kwargs["user"]
        self.password = quote_plus(kwargs["password"])
        self.database = kwargs["database"]
        c = f"mysql+pymysql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"
        self.engine = create_engine(c)

    def fetch_all_tables(self) -> set[str]:
        sql_query = "SELECT table_name AS tables FROM information_schema.tables WHERE table_schema = DATABASE()"
        df: DataFrame = pd.read_sql(sql_query, self.engine)
        names: Series[str] = df["tables"]
        names_set: set[str] = set(names.to_list())
        # print(names_set)
        return names_set

    def fetch_specify_sql_data(self, sql: str) -> tuple[DataFrame, list[str], int]:
        """执行sql获取数据,返回如下:
        replace_noneword False 表示不自动转换列名

        data frame;
        columns;
        rows;
        """

        data: DataFrame = pd.read_sql(sql, self.engine)
        columns: list[str] = data.columns.to_list()
        # print(type(data), columns, len(data))
        return (data, columns, len(data))

    def delete_auto_increment_column(self, df: DataFrame, pk: str = "id") -> DataFrame:
        """删除dataframe中的自增列"""
        df = df.drop(columns=pk)
        return df

    def insert_database_mysql(self, df: DataFrame, table_name: str) -> int:
        """将dataframe中的数据插入到mysql中"""
        row: int = df.to_sql(table_name, self.engine, if_exists="append", index=False)
        return row
