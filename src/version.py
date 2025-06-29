import datetime

VERSION = "0.0.1-beta.3"
APP_NAME = "GestroKey"
APP_DESCRIPTION = "一款手势控制工具"
BUILD_DATE = datetime.datetime.now().strftime("%Y-%m-%d")
AUTHOR = "xkaaaaa"
LICENSE = "GPL-3.0"

REPO_URL = f"https://github.com/{AUTHOR}/{APP_NAME}"

# Qt API 配置 (支持: "pyqt5", "pyqt6", "pyside2", "pyside6")
QT_API = "pyqt6"

VERSION_TYPE_RELEASE = "正式版"
VERSION_TYPE_PREVIEW = "预览版"
VERSION_TYPE_DEVELOPMENT = "未发布版"

CURRENT_VERSION_TYPE = VERSION_TYPE_DEVELOPMENT

ENABLE_PACKAGING = True
PACKAGE_WINDOWS = True
PACKAGE_MACOS = True
PACKAGE_LINUX = True
PACKAGE_STANDALONE = True
PACKAGE_PORTABLE = True

PACKAGER_WINDOWS = "nuitka"
PACKAGER_MACOS = "nuitka"
PACKAGER_LINUX = "nuitka"

PACKAGE_INCLUDE_DEBUG_SYMBOLS = False
PACKAGE_OPTIMIZE_LEVEL = 2
PACKAGE_COMPRESS_ASSETS = True
PACKAGE_UPXIFY = True

PACKAGE_OUTPUT_DIR = "dist"
PACKAGE_NAMING_PATTERN = "{app_name}-{version}-{platform}-{type}"


def get_version_string():
    return f"{APP_NAME} v{VERSION}"


def get_full_version_info():
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