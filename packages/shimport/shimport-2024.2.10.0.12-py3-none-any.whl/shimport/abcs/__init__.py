""" shimport.abc
"""

import itertools

from shimport.util import typing


# FIXME: move to fleks?
class FilterResult(typing.List[typing.Any]):
    """ """

    def map(self, fxn, logger: object = None):
        """ """
        return FilterResult(list(map(fxn, self)))

    def starmap(self, fxn, logger: object = None):
        """ """
        return FilterResult(list(itertools.starmap(fxn, self)))

    def prune(self, **kwargs):
        """ """
        result = FilterResult(filter(None, [x.prune(**kwargs) for x in self]))
        return result

    def filter(self, **kwargs):
        """ """
        return FilterResult([x.filter(**kwargs) for x in self])

    def __str__(self):
        return f"<{self.__class__.__name__} ({len(self)} items)>"

    __repr__ = __str__
