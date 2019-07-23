import pkg_resources


__version__ = pkg_resources.find_distributions('codado').version


__all__ = ["__version__"]
