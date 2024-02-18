""" shimport:

Module importing so dynamic, it's probably crazy.

Some features include:
    * lazy imports
    * import hooks
    * module "registries",
    * namespaces and namespace-filtering
    * fluent style
"""

from importlib import import_module  # noqa

from . import module

wrap = wrapper = namespace = module.wrapper  # noqa
lazy = lazy_import = module.lazy  # noqa
