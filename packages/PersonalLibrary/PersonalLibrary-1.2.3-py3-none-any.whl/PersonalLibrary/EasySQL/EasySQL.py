from typing import Self, Any

from PersonalLibrary.EasySQL.FieldType import FieldType
from PersonalLibrary.Initial import Logger
from PersonalLibrary.Initial import importModule
from PersonalLibrary.LibraryException.AccountException import AccountException
from PersonalLibrary.Text.Text import Text

if importModule('pymysql'):
    import pymysql


@Logger.ShowLogClass
class EasySQL:
    Logger.getLogger('EasySQL')
    Logger.info(Text().translate("info.easy_sql.connection_successfully"))

    def __init__(self, host: str = 'localhost', port: int = 3306, user: str = 'root', password: str = '<PASSWORD>',
                 db: str = None):
        self.host = host
        self.port = port
        self.user = user
        self.password = password

        try:
            self.connection = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.password)
            self.cursor = self.connection.cursor()
            self.fetchall = lambda: self.cursor.fetchall()
            self.db = db or 'root_sql'
            # 提交事务
            self.commit = lambda: self.connection.commit()
        except RuntimeError:
            Logger.error(Text().translate("error.easy_sql.connection_error.account_error"))
            raise AccountException()

    def _execute(self, cmd):
        Logger.debug(Text().of(cmd))
        self.cursor.execute(cmd)

    def createDatabase(self, dbName: str = 'root_sql') -> str:
        try:
            self._execute(f"CREATE DATABASE {dbName}")
            self.commit()
        except pymysql.err.ProgrammingError:
            Logger.error(Text().translate("error.easy_sql.create_database.db_name_already_exists").formatted(dbName))
        return dbName

    def switchDatabase(self, dbName: str) -> Self:
        self._execute(f'USE {dbName}')
        self.commit()
        return self

    @Logger.ShowLog
    def showDatabases(self) -> list:
        self._execute("SHOW DATABASES")
        result = "; ".join([i[0] for i in self.fetchall()])
        Logger.info(Text().of(result))
        return result.split('; ')

    @Logger.ShowLog
    def showTables(self) -> list:
        self._execute(f"SHOW TABLES")
        result = '; '.join([i[0] for i in self.fetchall()])
        Logger.info(Text().of(result))
        return result.split('; ')

    @Logger.ShowLog
    def showDatas(self, tableName: str, AND: bool = False, OR: bool = False, **conditions) -> list:
        Logger.info(Text().of(conditions))
        cmd = f"SELECT * FROM {tableName}"
        if conditions:
            cmd += " WHERE"
            cond_list = [f" {k}={v}" for k, v in conditions.items()]
            if AND and not OR:
                cmd += " AND".join(cond_list)
            elif OR and not AND:
                cmd += " OR".join(cond_list)
            else:
                Logger.error(Text().translate("error.easy_sql.sift_error"))
                return []

        self._execute(cmd)

        # 获取表头信息
        headers = [desc[0] for desc in self.cursor.description]

        # 获取内容
        result = self.fetchall()
        Logger.info(Text().of([dict(zip(headers, row)) for row in result]))
        return [dict(zip(headers, row)) for row in result]

    def deleteDatabases(self, databases: list[str] | str) -> None:
        if isinstance(databases, str):
            cmd = f"DROP DATABASE IF EXISTS {databases}"
            self._execute(cmd)
            self.commit()
            Logger.debug(Text().of(cmd))
        else:
            for database in databases:
                cmd = f"DROP DATABASE IF EXISTS {database}"
                self._execute(cmd)
                self.commit()
                Logger.info(Text().of(cmd))
        return None

    def deleteTables(self, tables: list[str] | str) -> None:
        if isinstance(tables, str):
            cmd = f"DROP TABLE IF EXISTS {tables}"
            self._execute(cmd)
            self.commit()
        else:
            for table in tables:
                cmd = f"DROP TABLE IF EXISTS {table}"
                self._execute(cmd)
                self.commit()

    def createTables(self, tableName: str, field: dict[str, FieldType], primary_key: str = None,
                     auto_increment: str = None, auto_increment_value: Any = None) -> Self:
        """
        创建表
        :param auto_increment_value: 自增值起始
        :param auto_increment: 自增键，默认为None
        :param primary_key: 主键，默认为None
        :param tableName: 表名
        :param field: {字段：类型}
        :return:
        """
        if auto_increment and auto_increment not in field:
            Logger.error(Text().translate('error.easy_sql.create_table.key_not_exist').formatted(auto_increment))
        if primary_key and primary_key not in field:
            Logger.error(Text().translate('error.easy_sql.create_table.key_not_exist').formatted(primary_key))

        fields = {key: value for key, value in field.items()}

        for key, value in field.items():
            if key == auto_increment and key == primary_key:
                fields[key] += " AUTO_INCREMENT PRIMARY KEY"
            elif key == auto_increment:
                fields[key] += " AUTO_INCREMENT"
            elif key == primary_key:
                fields[key] += " PRIMARY KEY"

        cmd = f"CREATE TABLE IF NOT EXISTS {tableName}"
        if fields:
            cmd += "(" + ", ".join([f"{key} {value}" for key, value in fields.items()]) + ")"
        else:
            ...

        if auto_increment_value is not None and auto_increment is not None:
            cmd += f" AUTO_INCREMENT = {auto_increment_value}"

        Logger.debug(Text().of(cmd))
        self._execute(cmd)
        self.commit()
        return self

    def addDatas(self, tableName: str, fields: dict[str, Any]):
        cmd = f"INSERT INTO {tableName} (" + ", ".join(fields.keys()) + ")"
        for key, value in fields.items():
            if isinstance(value, str):
                fields[key] = "'{}'".format(value)
        values = ", ".join(map(str, fields.values()))
        cmd += f" VALUES ({values})"
        self._execute(cmd)
        self.commit()
        return self

    def deleteDatas(self, tableName: str, conditions: dict, AND: bool = False, OR: bool = False):
        cmd = f"DELETE FROM {tableName} WHERE "

        if len(conditions) > 1:
            if AND and not OR:
                cmd += f"AND".join([f"{k}={v}" for k, v in conditions.items()])
            elif OR and not AND:
                cmd += f"OR".join([f"{k}={v}" for k, v in conditions.items()])
            else:
                Logger.error(Text().translate("error.easy_sql.sift_error"))
                return []
        else:
            cmd += f"{list(conditions.keys())[0]}={list(conditions.values())[0]}"
        self._execute(cmd)
        self.commit()
        return self

    def SQLCommand(self, cmd: str):
        try:
            self._execute(cmd)
        except pymysql.err.ProgrammingError:
            Logger.error(Text().translate("error.easy_sql.grammatical_errors").formatted(cmd))


if __name__ == "__main__":
    sql = EasySQL(password='wang12345')
    sql.SQLCommand("Hello World")
