"""
GestroKey UI模块
提供应用程序的用户界面组件
"""

# 从version模块导入版本信息
try:
    from version import VERSION
except ImportError:
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from version import VERSION

__version__ = VERSION 