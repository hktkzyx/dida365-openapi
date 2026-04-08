"""Dida365 OpenAPI CLI package."""

from importlib.metadata import PackageNotFoundError, version

__all__ = ["__version__"]

try:
    __version__ = version("dida365-openapi")
except PackageNotFoundError:
    __version__ = "0+unknown"
