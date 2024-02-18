from .version import __version__
from .matplotlib import configure as configure_matplotlib

__all__ = ["__version__"]

configure_matplotlib()
