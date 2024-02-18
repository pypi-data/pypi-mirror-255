""" shimport.util
"""

import importlib

from shimport.abcs.attrdict import AttrDict


def get_namespace(name):
    """ """

    class ModuleNamespace(AttrDict):
        """ """

        def __str__(self):
            return f"<{self.__class__.__name__}[{self.__class__.name}]>"

        __repr__ = __str__

        @property
        def module(self):
            result = importlib.import_module(self.__class__.name)
            return result

    ModuleNamespace.name = name
    return ModuleNamespace()
