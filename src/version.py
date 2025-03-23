"""
GestroKey 版本信息模块

该模块包含GestroKey应用程序的版本信息和元数据。
在项目中导入这个模块来获取当前版本号和其他版本相关信息。
"""

# 版本信息 (遵循语义化版本 https://semver.org/)
__version__ = "1.0.0"
__version_name__ = "稳定版"  # 版本名称，例如："Alpha", "Beta", "RC", "稳定版"

# 项目元数据
__title__ = "GestroKey"
__description__ = "一款基于鼠标手势的自动化工具"
__author__ = "xkaaaaa"
__author_email__ = ""  # 可选
__copyright__ = "© 2025 xkaaaaa"
__license__ = "GPLv3"  # 许可证类型
__url__ = "https://github.com/xkxkaaaaa/GestroKey.git"

# 构建信息
__build_date__ = None  # 构建日期，可在构建时设置

# 函数接口
def get_version():
    """获取完整的版本字符串
    
    Returns:
        str: 格式化的版本字符串
    """
    return f"{__version__} ({__version_name__})"

def get_about_text():
    """获取格式化的关于信息文本
    
    Returns:
        str: 包含版本和版权信息的格式化文本
    """
    return (
        f"{__title__} v{__version__} {__version_name__}\n"
        f"{__description__}\n\n"
        f"{__copyright__}\n"
        f"项目地址: {__url__}"
    ) 