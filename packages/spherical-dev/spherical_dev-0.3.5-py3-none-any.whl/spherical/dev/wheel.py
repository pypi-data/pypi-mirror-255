# flake8: noqa
try:
    from .release import wheel
except ImportError:
    from .utils import release_warning as wheel
