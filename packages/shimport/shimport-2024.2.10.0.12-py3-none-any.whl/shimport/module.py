""" shimport.module
"""

from shimport.util import typing

from . import models

MODULE_REGISTRY = dict()


class ModuleBuilder(models.ModulesWrapper):
    # @typing.validate_arguments
    def __init__(
        self,
        name: str = "",
        init_hooks: typing.List = [],
        assign_objects: bool = True,
        **kwargs,
    ):
        models.ModulesWrapper.__init__(self, name=name, **kwargs)
        self.init_hooks = init_hooks
        self.assign_objects = assign_objects

    def initialize(self, **filters):
        """

        :param **filters:

        """
        # FIXME: leaky abstraction
        msg = f"Building module-registry for {self.name}.."
        [h(msg) for h in self.init_hooks]
        return self.filter(**filters)

    def namespace_modified_hook(self, assignment, val):
        if self.assign_objects:
            self.validate_assignment(assignment)
            setattr(self.module, assignment, val)

    def filter(self, **filter):
        """

        :param **filter:

        """
        models.ModulesWrapper.filter(self, **filter)
        self.logger.info(f"imported {len(self.namespace)} items to {self.name}")


def module_builder(
    name: str,
    return_objects=False,
    assign_objects: bool = True,
    sort_objects: typing.Dict = {},
    **kwargs,
) -> None:
    """

    :param name: str:
    :param return_objects: Default value = False)
    :param assign_objects: bool:  (Default value = True)
    :param sort_objects: typing.Dict:  (Default value = {})
    :param name: str:
    :param assign_objects: bool:  (Default value = True)
    :param sort_objects: typing.Dict:  (Default value = {})
    :param **kwargs:

    """
    if name not in MODULE_REGISTRY:
        MODULE_REGISTRY[name] = ModuleBuilder(name=name, **kwargs)
    builder = MODULE_REGISTRY[name]
    builder.initialize()
    result = builder.namespace
    result = result.values() if return_objects else result
    result = sorted(result, **sort_objects) if sort_objects else result
    return result


builder = module_builder
build = builder


def wrap(name, **kwargs):
    """
    :param name:
    :param **kwargs:
    """
    """ """
    """ """
    """ """
    """ """
    # from types import ModuleType
    if isinstance(name, (typing.ModuleType)):
        mod = name
        name = mod.__name__
        # kwargs['import_mods'] = list(set(kwargs.pop('import_mods',[])+[name]))
    result = models.ModulesWrapper(name, import_names=[f"{name}.*"], **kwargs)
    return result


wrapper = wrap


def lazy(
    module_name: str,
) -> models.LazyModule:
    """

    :param module_name: str:
    :param module_name: str:

    """
    assert module_name
    return models.LazyModule(module_name)
