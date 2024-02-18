""" shimport.models
"""

import os
import glob
import inspect
import logging
import importlib
import itertools
import collections
from pathlib import Path

from shimport.util import lme, typing

from .abcs import FilterResult
from .util import get_namespace

LOGGER = lme.get_logger(__name__)

import_spec = collections.namedtuple(
    "importSpec", "assignment var star package relative"
)
# from typing import ItemsView


class ModulesWrapper:
    """ """

    class Error(ImportError):
        """ """

    def __init__(
        self,
        name: str = "",
        import_mods: typing.List[str] = [],
        import_names: typing.List[str] = [],
        import_subs: typing.List[str] = [],
        import_children: bool = False,
        # lazy: bool = False,
        filter_failure_raises: bool = True,
        logger=None,
        **kwargs,
    ):
        """ """
        assert name
        self.name = name
        self.import_mods = import_mods
        self.import_names = import_names
        self.logger = logger or logging.getLogger(__name__)
        self.import_subs = import_subs
        self.import_children = import_children
        self.namespace = get_namespace(name)
        self.filter_failure_raises = filter_failure_raises
        if kwargs:
            raise TypeError(f"extra kwargs: {kwargs}")

    def items(self) -> typing.ItemsView[str, typing.Any]:
        return self.namespace.items()

    def map_ns(self, fxn) -> FilterResult:
        """ """
        return FilterResult(itertools.starmap(fxn, self.namespace.items()))

    def map(self, *args, **kwargs):
        return self.map_ns(*args, **kwargs)

    def normalize_import(self, name):
        """

        :param name:

        """
        assignment = None
        if " as " in name:
            name, assignment = name.split(" as ")
        relative = name.startswith(".")
        name = name if not relative else name[1:]
        bits = name.split(".")
        if len(bits) == 1:
            package = var = bits.pop(0)
        else:
            var = bits.pop(-1)
            package = ".".join(bits)
        if relative:
            package = f"{self.name}.{package}"
        result = import_spec(
            assignment=assignment,
            var=var,
            star="*" in var,
            package=package,
            relative=relative,
        )
        return result

    @property
    def module(self):
        """ """
        result = importlib.import_module(self.name)
        return result

    def do_import(self, package):
        """

        :param package:

        """
        return importlib.import_module(package)

    @property
    def parent_folder(self):
        """ """
        return Path(self.module.__file__).parents[0]

    @property
    def parent(self):
        """ """
        return self.__class__(name=".".join(self.name.split(".")[:-1]))

    def select(self, **filter_kwargs):
        """

        :param **filter_kwargs:

        """
        tmp = list(self.filter(**filter_kwargs))
        assert len(tmp) == 1
        return tmp[0]

    def validate_assignment(self, assignment):
        """

        :param assignment:

        """
        if assignment in dir(self.module):
            msg = f"refusing to override existing value in target module: {assignment}"
            self.logger.critical(msg)
            err = f"cannot assign name `{assignment}` to {self.module}; already exists!"
            raise ModulesWrapper.Error(err)

    def assign_back(self):
        """ """
        for assignment in self.namespace:
            self.validate_assignment(assignment)
            setattr(self.module, assignment, self.namespace[assignment])

    def prune(self, **filters):
        """
        Like `filter`, except modifies this wrapper in-place.
        """
        # self.logger.critical(f"prune: {filters}")
        self.namespace = self.filter(**filters)
        # return self if self.namespace else None
        return self

    def sorted(self, key=None):
        tmp = self.namespace.items()
        tmp = sorted(tmp, key=key)
        self.namespace = collections.OrderedDict(tmp)
        return self

    def get_folder_children(
        self,
        include_main: str = True,
        exclude_private=True,
    ):
        """ """
        p = self.parent_folder / "**/*.py"
        result = glob.glob(str(p))
        result = [Path(x) for x in result]
        main = [x for x in result if x.stem == "__main__"]
        if exclude_private:
            result = [x for x in result if not x.stem.startswith("_")]
        if include_main:
            result += main
        children = []
        for p in result:
            rel = p.relative_to(self.parent_folder)
            rel = rel.parents[0] / rel.stem
            rel = str(rel).replace(os.path.sep, ".")
            dotpath = f"{self.name}.{rel}"
            child = ModulesWrapper(
                name=dotpath, import_mods=[dotpath], import_names=[f"{dotpath}.*"]
            )
            children.append(child)
        return children

    def filter_folder(
        self,
        prune: typing.Dict = {},
        filter: typing.Dict = {},
        select: typing.Dict = {},
        **kwargs,
    ):
        """ """
        children = FilterResult(self.get_folder_children(**kwargs))
        if sum([1 for choice in map(bool, [filter, select, prune]) if choice]) == 0:
            return children
        else:
            result = []
            if sum([1 for choice in [filter, select, prune] if bool(choice)]) == 1:
                filter_results = []
                if filter:
                    fxn, kwargs = children.filter, filter
                if select:
                    fxn, kwargs = children.select, select
                if prune:
                    fxn, kwargs = children.prune, prune
                children = FilterResult(fxn(**kwargs))
                return children
        return FilterResult(result)

    def __items__(self):
        """ """
        return self.namespace.__items__()

    def _apply_filters(
        self,
        filter_vals=[],
        filter_names=[],
        import_statements=[],
        rekey: typing.Callable = None,
    ) -> typing.Dict:
        """ """
        module = self.module
        namespace = {}
        import_statements = import_statements or self.import_side_effects()
        for st in import_statements:
            submod = self.do_import(st.package)
            vars = dir(submod) if st.star else [st.var]
            for var in vars:
                assert isinstance(var, str), var
                for validator in filter_names:
                    if not self.run_filter(validator, var):
                        break
                else:  # name is ok
                    val = getattr(submod, var)
                    for validator in filter_vals:
                        if not self.run_filter(validator, val):
                            break
                    else:  # name/val is ok
                        assignment = st.assignment or var
                        namespace[assignment] = val
                        self.namespace_modified_hook(assignment, val)
        if rekey:
            return dict([rekey(v) for v in namespace.values()])
        return namespace

    def filter(
        self,
        exclude_private: bool = True,
        name_is: str = "",
        filter_names: typing.List[typing.Callable] = [],
        filter_vals: typing.List[typing.Callable] = [],
        types_in: typing.List[type(type)] = [],
        filter_module_origin: str = "",
        name_predicate: typing.Callable = None,
        val_predicate: typing.Callable = None,
        only_functions: bool = False,
        only_data: bool = False,
        only_classes: bool = False,
        filter_instances: typing.List[type(type)] = [],
        exclude_names: typing.List[str] = [],
        **kwargs,
    ) -> typing.Dict:
        """
        Constructs
        """
        if name_is:
            filter_names = [lambda name: name == name_is] + filter_names
        if exclude_private:
            filter_names = [lambda name: not name.startswith("_")] + filter_names

        if exclude_names:
            filter_names = [
                lambda n: n not in exclude_names,
            ] + filter_names

        filter_vals = filter_vals
        if types_in:
            filter_vals = [
                lambda val: any([typing.is_subclass(val, ty) for ty in types_in])
            ] + filter_vals
        if only_functions:
            filter_vals = [
                lambda val: all([callable(val), not inspect.isclass(val)])
            ] + filter_vals
        if only_classes:
            filter_vals = [inspect.isclass] + filter_vals
        if only_data:
            filter_vals = [
                lambda val: not any(
                    [
                        # no instances, classes, or function
                        # hasattr(val, "__class__"),
                        type(val).__name__
                        in [
                            "module",
                        ],
                        inspect.isclass(val),
                        callable(val),
                    ]
                )
            ] + filter_vals
        if name_predicate:
            filter_names = [name_predicate] + filter_names
        if val_predicate:
            filter_vals = [val_predicate] + filter_vals
        if filter_instances:
            filter_vals = [lambda val: isinstance(val, filter_instances)] + filter_vals
        if filter_module_origin:
            filter_module_origin = (
                self.name if filter_module_origin is True else filter_module_origin
            )
            filter_vals = [
                lambda val: filter_module_origin == getattr(val, "__module__", None)
            ] + filter_vals
        return self._apply_filters(
            filter_vals=filter_vals,
            filter_names=filter_names,
            **kwargs,
        )

    def run_filter(self, validator, arg) -> typing.BoolMaybe:
        """
        Wrapper to honor `filter_failure_raises`
        """
        test = False
        try:
            test = validator(arg)
        except:
            if self.filter_failure_raises:
                raise
        return test

    def namespace_modified_hook(self, assignment, val) -> typing.NoneType:
        """ """

    def do_import_name(self, arg) -> object:
        tmp = self.normalize_import(arg)
        return self

    def import_side_effects(
        self,
    ) -> typing.List[str]:
        """ """
        import pathlib

        import_statements = []
        for name in self.import_mods:
            spec = self.normalize_import(name)
            assignment = spec.assignment or spec.var
            LOGGER.critical(f"importing {spec.package}")
            submod = importlib.import_module(spec.package)
            self.namespace[assignment] = submod
            self.namespace_modified_hook(assignment, submod)

        for name in self.import_names:
            import_statements.append(self.normalize_import(name))
            self.do_import_name(name)

        if self.import_children:
            import_pattern = (
                self.import_children
                if isinstance(self.import_children, (str, pathlib.Path))
                else "*.py"
            )
            mod_file = self.module.__file__
            children = []
            folder = Path(mod_file).parents[0]
            children = folder.glob(import_pattern)
            for child in children:
                if not child.stem.startswith("__"):
                    child = str(Path(child).relative_to(folder))[: -len(".py")]
                    child = child.replace("/", ".")
                    self.import_subs.append(child)

        for name in self.import_subs:
            import_statements.append(self.normalize_import(f".{name}.*"))
        import_statements = list(set(import_statements))
        return import_statements

    def __str__(self) -> str:
        return f"<{self.__class__.__name__}[{self.name}]>"

    __repr__ = __str__


class LazyModule:
    """ """

    class LazyImportError(ImportError):
        pass

    class LazyResolutionError(LazyImportError):
        pass

    def __init__(self, module_name: str = ""):
        """ """
        assert module_name
        self.module_name = module_name
        self.module = None

    def resolve(self):
        """ """
        if self.module is None:
            try:
                self.module = importlib.import_module(self.module_name)
            except (ImportError,) as exc:
                raise LazyModule.LazyResolutionError(exc)

    def __getattr__(self, var_name):
        """ """
        self.resolve()
        return getattr(self.module, var_name)

    def __repr__(self):
        return f"<LazyModule[{self.module_name}]>"

    __str__ = __repr__
