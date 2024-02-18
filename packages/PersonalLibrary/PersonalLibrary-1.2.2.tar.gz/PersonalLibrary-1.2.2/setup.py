from setuptools import setup, find_packages

setup(
    name='PersonalLibrary',  # 库的名称
    version='1.2.2',  # 库的版本号
    author='XichengWu',  # 作者姓名
    author_email='mcht1023@gmail.com',  # 作者邮箱
    description='A collection of libraries or packages that are commonly used by some individuals',  # 库的简短描述
    url='https://gitee.com/XichengWu/personal-library',  # 你的库的代码仓库地址
    packages=find_packages(),  # 包含的包或模块的列表
    package_data={'PersonalLibrary': [r'E:\Python\PersonalLibrary\EasyTkinter\resource\assets\icon\icon.png',
                                      r'E:\Python\PersonalLibrary\Text\assets\lang\zh_cn.json',
                                      r'E:\Python\PersonalLibrary\Config\assets\config.json']},
    install_requires=[],  # 依赖项的列表
)
