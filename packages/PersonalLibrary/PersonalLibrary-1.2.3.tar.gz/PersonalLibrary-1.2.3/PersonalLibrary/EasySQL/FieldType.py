class FieldType(str):
    """
    TINYINT：范围为 -128 到 127 或 0 到 255（无符号）。
    SMALLINT：范围为 -32768 到 32767 或 0 到 65535（无符号）。
    INT：范围为 -2147483648 到 2147483647 或 0 到 4294967295（无符号）。
    BIGINT：范围为 -9223372036854775808 到 9223372036854775807 或 0 到 18446744073709551615（无符号）。
    浮点数类型（Floating-Point Types）：
    FLOAT：单精度浮点数。
    DOUBLE：双精度浮点数。
    定点数类型（Decimal Types）：
    DECIMAL：精确小数，可指定精度和小数位数。
    字符串类型（String Types）：
    CHAR：定长字符串。
    VARCHAR：可变长度字符串。
    TEXT：长文本字符串。
    日期和时间类型（Date and Time Types）：
    DATE：日期，格式为 'YYYY-MM-DD'。
    TIME：时间，格式为 'HH:MM:SS'。
    DATETIME：日期和时间，格式为 'YYYY-MM-DD HH:MM:SS'。
    TIMESTAMP：时间戳，记录了自1970年1月1日以来的秒数。
    """
    TINYINT = "TINYINT"
    SMALLINT = "SMALLINT"
    INT = "INT"
    BIGINT = "BIGINT"
    FLOAT = "FLOAT"
    DOUBLE = "DOUBLE"
    DECIMAL = "DECIMAL"
    CHAR = "CHAR"
    VARCHAR = lambda d: f"VARCHAR({d})"
    TEXT = "TEXT"
    DATE = "DATE"
    TIME = "TIME"
    DATETIME = "DATATIME"
    TIMESTAMP = "TIMESTAMP"
