# flake8: noqa
try:
    from .release import devpi_release as release
except ImportError:
    from .utils import release_warning as release
