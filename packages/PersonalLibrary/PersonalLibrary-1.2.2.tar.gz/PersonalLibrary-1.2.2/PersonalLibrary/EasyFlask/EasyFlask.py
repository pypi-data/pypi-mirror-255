import secrets
from typing import Self

from PersonalLibrary.Config.Config import Config
from PersonalLibrary.LibraryException.FlaskMethodException import FlaskMethodException
from PersonalLibrary.Initial import importModule, Logger
from PersonalLibrary.Text.Text import Text

if importModule("flask"):
    from flask import *

    Logger.hide_log()


def _EmptyFunction():
    return None


@Logger.ShowLogClass
class EasyFlask:
    AppName = __name__
    app = Flask(AppName)

    def __init__(self):
        """
        不接受带参数的函数
        """
        Logger.getLogger(self.__class__.__name__)
        self.static_folder = './resources/static'
        self.template_folder = './resources/templates'
        self.assets_folder = './resources/assets'

        self.app_config: dict | Config = self.app.config  # 设置文件
        self.debug: bool = False  # DEBUG模式
        self.testing: bool = False  # TESTING模式
        self.send_file_max_age_default: int = 0  # 发送静态文件时，设置缓存的最长时间
        self.secret_key: str = secrets.token_hex(16)  # 生成一个包含16个随机字节的十六进制字符串

        self.routeMethods = ['GET', 'POST']
        self.GET = [self.routeMethods[0]]
        self.POST = [self.routeMethods[1]]

        self.routeUrlToRule: dict = dict()
        self.routeUrlToFunc: dict = dict()

        self.routeDict: dict[str, callable] = dict()
        self.redirectDict: dict[str, str] = dict()

    def _addRouteUrl(self, func: callable, routePath: str) -> None:
        """
        添加路由地址所对应的函数端口
        :param func: 函数
        :param routePath: 路由地址
        :return:
        """
        self.routeUrlToRule[routePath] = func.__name__
        self.routeUrlToFunc[func.__name__] = routePath

    def _checkMethod(self, methods: list[str]) -> None:
        if methods is None:
            methods = ['GET']
        if self.GET[0] not in methods and self.POST[0] not in methods:
            Logger.error(Text().translate("error.flask.route.method_not_allowed").formatted(methods, self.routeMethods))
            raise FlaskMethodException(
                Text().translate("error.flask.route.method_not_allowed").formatted(methods, self.routeMethods))

    def _checkRoute(self, func: callable, rule, methods, toRulePath=None) -> bool:
        """
        检查toRulePath是否已经存在
        :param func: 函数
        :param rule: 路由地址
        :param methods: 请求方法
        :param toRulePath: 重定向路由地址
        :return: bool
        """
        if toRulePath is None:
            # 检查的是rule的地址
            toRulePath = rule
        self._checkMethod(methods)
        if toRulePath in list(self.routeUrlToRule.values()) and toRulePath not in self.redirectDict:  # 在路由列表不在重定向列表
            return True  # 存在
        else:
            self._addRouteUrl(func, rule)  # 添加到路由列表中
            return False  # 不存在

    def run(self, host: str = '127.0.0.1', port: int = 5000):
        self._setConfig()
        self.app.run(host=host, port=port)

    def _setConfig(self):
        self.app_config: dict | Config = self.app.config.update({
            'debug'.upper(): self.debug,
            'testing'.upper(): self.testing,
            'send_file_max_age_default'.upper(): self.send_file_max_age_default,
            'secret_key'.upper(): self.secret_key
        })

    def updateConfig(self, appConfig: dict) -> Self:
        self.app_config.update(appConfig)
        return self

    def easyRoute(self, rule: str, methods: list[str], func: callable, **options):
        """
        最简单不带参数的路由
        :param rule: 路由地址
        :param methods: 请求方法
        :param func: 实现函数端口
        :return: null
        """
        if self._checkRoute(func, rule, methods):
            # 如果存在这个路由
            Logger.warning(Text().translate("warning.flask.route_already_exist").formatted(func.__name__, rule,
                                                                                           self.routeUrlToFunc[
                                                                                               func.__name__]))
            return None  # 不创建这个路由
        # 如果不存在
        self.routeDict[rule] = func
        self.app.route(rule=rule, methods=methods, **options)(self.routeDict[rule])  # 创建路由

    def easyRedirect(self, rule: str, methods: list[str], toRulePath: str, isInnerWeb: bool = True, **options):
        """
        最简单重定向
        :param isInnerWeb: 是否是内部网址
        :param rule: 路由地址
        :param methods: 请求方法
        :param toRulePath: 重定向后的路由地址
        :param options: 其他方法
        :return:
        """
        if rule not in self.redirectDict:
            self.redirectDict[rule] = toRulePath

        if toRulePath not in self.routeDict:
            Logger.warning(Text().translate("warning.flask.route_not_exist").formatted(toRulePath))

        def forRedirect():
            if isInnerWeb:
                return redirect(url_for(self.routeDict[toRulePath].__name__))
            else:
                return redirect(toRulePath)

        forRedirect.__name__ = f'{rule}_redirect'  # 设置函数名称
        self._addRouteUrl(forRedirect, rule)
        self.app.add_url_rule(rule, None, forRedirect, methods=methods, **options)


if __name__ == "__main__":
    def Index():
        return "Hello World!"


    def Hello():
        return "Hello World!"


    def Name(name):
        return f"Hello {name}"


    easyFlask = EasyFlask()
    easyFlask.debug = True
    easyFlask.easyRoute('/index', ['GET'], Index)
    easyFlask.easyRoute('/hello', ['GET'], Hello)
    easyFlask.easyRoute('/<string:name>', ['GET'], Name)
    easyFlask.easyRedirect('/', ['GET'], '/index')
    easyFlask.easyRedirect('/home', ['GET'], '/hello')
    easyFlask.run()
