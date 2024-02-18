""" shimport.abcs.attrdict
"""

from shimport.util import lme, typing

LOGGER = lme.get_logger(__name__)


class AttrDictBase:
    """A dictionary with attribute-style access.
    It maps attribute access to the real dictionary.


    """

    def __init__(self, **init: typing.OptionalAny):
        dict.__init__(self, init)

    def __getattr__(self, name: str) -> typing.Any:
        try:
            return super().__getitem__(name)
        except (KeyError,) as exc:
            LOGGER.info(f"AttrDict: KeyError accessing {name}")
            raise AttributeError(exc)

    def __setitem__(self, key: str, value: typing.Any) -> typing.Any:
        return super().__setitem__(key, value)

    __setattr__ = __setitem__

    def __getitem__(self, name: str) -> typing.Any:
        try:
            return super().__getitem__(name)
        except (KeyError,) as exc:
            LOGGER.info(f"AttrDict: KeyError accessing {name}")
            raise KeyError(exc)

    def __delitem__(self, name: str) -> typing.Any:
        return super().__delitem__(name)

    def __getstate__(self) -> typing.Iterable:
        return self.__dict__.items()

    def __setstate__(self, items: typing.Any) -> None:
        for key, val in items:
            self.__dict__[key] = val

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({dict.__repr__(self)})"

    # def as_dict(self):
    #     return dict([[key,getattr(self,key)] for key in self])


class AttrDict(AttrDictBase, dict):
    pass
