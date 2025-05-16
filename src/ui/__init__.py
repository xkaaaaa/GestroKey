"""
GestroKey UI模块
提供应用程序的用户界面组件
"""

# 从version模块导入版本信息
try:
    from version import VERSION
except ImportError:
    import os
    import sys

    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from version import VERSION

# 导出模块
from ui.splash_screen import SplashScreen

__version__ = VERSION
