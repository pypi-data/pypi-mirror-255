Name = "Exception"
Version = "1.0.0"
Author = "WuxiCheng"
Description = "Predictable errors in the personal library"

ErrorCode = 10000


def getErrorCode():
    global ErrorCode
    ErrorCode += 1
    return ErrorCode
