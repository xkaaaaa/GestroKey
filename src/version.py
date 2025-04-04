"""
GestroKey版本信息模块
此模块存储所有随时间变化的变量，如版本号、构建日期等
"""
import datetime

# 版本信息
VERSION = "2.0.0"
VERSION_NAME = "第二个版本"
BUILD_DATE = "6666-06-06"  # 格式：YYYY-MM-DD
BUILD_NUMBER = 1

# 应用信息
APP_NAME = "GestroKey"
APP_DESCRIPTION = "一款手势控制工具"
AUTHOR = "xkaaaaa"
COPYRIGHT = f"© {datetime.datetime.now().year} {AUTHOR}"

# 其他可能随时间变化的变量
DEFAULT_PEN_WIDTH = 3
DEFAULT_PEN_COLOR = [0, 120, 255]  # RGB格式

def get_version_string():
    """获取格式化的版本字符串"""
    return f"v{VERSION}"

def get_full_version_string():
    """获取完整的版本字符串，包含版本名称和构建信息"""
    return f"v{VERSION} ({VERSION_NAME}) - 构建 #{BUILD_NUMBER}"

def get_about_text():
    """获取关于信息文本"""
    return f"""{APP_NAME} {get_version_string()}
{APP_DESCRIPTION}
{COPYRIGHT}
构建日期: {BUILD_DATE}
构建编号: {BUILD_NUMBER}
""" 