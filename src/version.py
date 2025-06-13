"""
版本信息模块

此模块提供GestroKey应用程序的版本信息和应用名称，
集中管理版本号和应用相关信息。
"""
import datetime

# 版本信息
VERSION = "0.0.1-beta.2"
APP_NAME = "GestroKey"
APP_DESCRIPTION = "一款手势控制工具"
BUILD_DATE = datetime.datetime.now().strftime("%Y-%m-%d")
AUTHOR = "xkaaaaa"
LICENSE = "GPL-3.0"

# 仓库地址
REPO_URL = f"https://github.com/{AUTHOR}/{APP_NAME}"

# Qt API 配置 (支持: "pyqt5", "pyqt6", "pyside2", "pyside6")
QT_API = "pyqt6"

# 版本类型
VERSION_TYPE_RELEASE = "正式版"  # 正式发布版本
VERSION_TYPE_PREVIEW = "预览版"  # 预览版本
VERSION_TYPE_DEVELOPMENT = "未发布版"  # 开发中版本

# 当前版本类型
CURRENT_VERSION_TYPE = VERSION_TYPE_DEVELOPMENT

# 打包配置选项
# 总体控制
ENABLE_PACKAGING = True  # 是否启用打包流程

# 平台特定控制
PACKAGE_WINDOWS = True  # 是否打包Windows版本
PACKAGE_MACOS = True  # 是否打包macOS版本
PACKAGE_LINUX = True  # 是否打包Linux版本

# 打包类型控制
PACKAGE_STANDALONE = True  # 是否生成单文件版本
PACKAGE_PORTABLE = True  # 是否生成便携版本

# 打包工具选择
PACKAGER_WINDOWS = "pyinstaller"  # Windows打包工具: "nuitka" 或 "pyinstaller"
PACKAGER_MACOS = "pyinstaller"  # macOS打包工具: 仅支持 "pyinstaller"
PACKAGER_LINUX = "pyinstaller"  # Linux打包工具: "nuitka" 或 "pyinstaller"

# 打包参数配置
PACKAGE_INCLUDE_DEBUG_SYMBOLS = False  # 是否包含调试符号
PACKAGE_OPTIMIZE_LEVEL = 2  # 优化级别 (0-2)
PACKAGE_COMPRESS_ASSETS = True  # 是否压缩资源文件
PACKAGE_UPXIFY = True  # 是否使用UPX压缩可执行文件

# 输出控制
PACKAGE_OUTPUT_DIR = "dist"  # 输出目录名称
# 命名模式: 可以使用 {app_name}, {version}, {platform}, {type} 作为占位符
PACKAGE_NAMING_PATTERN = "{app_name}-{version}-{platform}-{type}"


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
        "version_type": CURRENT_VERSION_TYPE,
        "app_name": APP_NAME,
        "description": APP_DESCRIPTION,
        "build_date": BUILD_DATE,
        "author": AUTHOR,
        "license": LICENSE,
        "repo_url": REPO_URL,
    }


def get_packaging_config():
    """
    获取打包配置信息

    返回:
        dict: 包含打包配置的字典
    """
    return {
        "enable_packaging": ENABLE_PACKAGING,
        "platforms": {
            "windows": {
                "enabled": PACKAGE_WINDOWS,
                "packager": PACKAGER_WINDOWS,
            },
            "macos": {
                "enabled": PACKAGE_MACOS,
                "packager": PACKAGER_MACOS,
            },
            "linux": {
                "enabled": PACKAGE_LINUX,
                "packager": PACKAGER_LINUX,
            },
        },
        "package_types": {
            "standalone": PACKAGE_STANDALONE,
            "portable": PACKAGE_PORTABLE,
        },
        "output": {"dir": PACKAGE_OUTPUT_DIR, "naming_pattern": PACKAGE_NAMING_PATTERN},
        "options": {
            "debug_symbols": PACKAGE_INCLUDE_DEBUG_SYMBOLS,
            "optimize_level": PACKAGE_OPTIMIZE_LEVEL,
            "compress_assets": PACKAGE_COMPRESS_ASSETS,
            "use_upx": PACKAGE_UPXIFY,
        },
    }


# 测试代码
if __name__ == "__main__":
    print(get_version_string())
    print(get_full_version_info())
    print(get_packaging_config())
