try:
    from version import VERSION
except ImportError:
    import os
    import sys

    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from version import VERSION

__version__ = VERSION
