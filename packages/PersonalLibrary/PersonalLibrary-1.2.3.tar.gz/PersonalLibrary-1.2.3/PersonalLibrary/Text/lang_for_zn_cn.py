import os.path

_lang_file = """{
  "error.import.not_exist": "无法导入指定模块（{}），请确认是否安装",
  "error.requests.method": "未知访问方法，目前只支持 requests | post",
  "error.requests.not_exist": "请求URL未响应，请检查",
  "error.requests.response_json_not_exist": "响应中未包含json内容",
  "info.requests.response.status_code": "响应成功，响应代码：{}",
  "error.requests.connect_timeout": "请求时间超时，请检查请求网址（{}）是否正常，若正常，请设置超时时间，目前超时时间是：{} (s)",
  "info.requests.response.text": "获取到响应的网页数据",
  "warning.unicode_encode_error": "无法解密该内容，请尝试更换解码集重试，失败内容：{}，目前所用的解码集encode：{}，decode：{}",
  "error.progress.html_is_none": "获取到的HTML内容为空，请重试",
  "error.requests.web_connection": "测试网页请求失败，请检查网络环境",
  "error.connection": "链接失败，请检查网络环境",
  "error.flask.route.method_not_allowed": "{}方法不属于{}中的任意一种",
  "error.flask.route_method": "未知请求方法，请检查",
  "warning.flask.route_already_exist": "{}路由的地址'{}'已经被{}使用，请更改!",
  "warning.flask.route_not_exist": "{}路由不存在，无法进行重定向，请检查！",
  "error.tkinter.controller_not_supported": "未知{}控件，目前只支持以下控件{}",
  "info.tkinter.show": "显示成功！",
  "error.tkinter.controller_not_build": "{}：{}控件还未构建,请检查",
  "error.tkinter.controller_already_exist": "{}：{}控件早已存在，请更换名称",
  "error.tkinter.missing_arguments": "缺少参数{}，请在装饰器上添加这个参数以保证正常运行",
  "warning.tray.menu_name_already_exists": "{}菜单名早已存在，请更换名字",
  "info.tray.menu_start": "启动托盘",
  "error.config_option_exception": "设置的{}不存在于config可支持的范围，请使用Config().get()查询支持的选项",
  "error.tkinter.image_not_found": "{}图片不存在，请检查",
  "error.tkinter.unknown_option":"未知控件：{}",
  "error.easy_sql.sift_error": "AND与OR筛选条件不能共存，返回为[]",
  "info.easy_sql.connection_successfully": "建立MySQL链接成功",
  "error.easy_sql.create_table.key_not_exist": "{}键值不存在，请检查",
  "error.easy_sql.connection_error.account_error": "账户或密码错误，请检查！",
  "error.easy_sql.grammatical_errors": "{}中存在语法错误，请检查！"
}
"""

_path = os.path.abspath(__file__).split('lang_for_zn_cn.py')[0] + 'assets\\lang'

# E:\Python\PersonalLibrary\PersonalLibrary\Text

if not os.path.exists(_path):
    os.mkdir(_path)
    _path += "\\lang"
    print(_path)
    os.mkdir(_path)


def writeLang():
    with open(_path + '\\zh_cn.json', 'w', encoding='utf-8') as f:
        f.write(_lang_file)
