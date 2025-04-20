"""
版本信息模块

此模块提供GestroKey应用程序的版本信息和应用名称，
集中管理版本号和应用相关信息。
"""
import datetime

# 版本信息
VERSION = "0.0.1"
APP_NAME = "GestroKey"
APP_DESCRIPTION = "一款手势控制工具"
BUILD_DATE = datetime.datetime.now().strftime("%Y-%m-%d")
AUTHOR = "xkaaaaa"
LICENSE = "GPL-3.0"

def get_version_string():
    """
    获取格式化的版本字符串
    
    返回:
        str: 格式化的版本信息，包含版本号和应用名称
    """
    return f"{APP_NAME} v{VERSION}"

def get_full_version_info():
    """
    获取完整的版本信息
    
    返回:
        dict: 包含版本号、应用名称、构建日期等信息的字典
    """
    return {
        "version": VERSION,
        "app_name": APP_NAME,
        "description": APP_DESCRIPTION,
        "build_date": BUILD_DATE,
        "author": AUTHOR,
        "license": LICENSE
    }

# 测试代码
if __name__ == "__main__":
    print(get_version_string())
    print(get_full_version_info())