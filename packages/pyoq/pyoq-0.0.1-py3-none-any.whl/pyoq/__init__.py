import sys

from .query import query as pyoq


#
# HACK: this hack allows to use pyoq like a function instead of a module.
#       e.g.:
#       import pyoq
#       pyoq(
#           {"top": {"middle": {"nested": "value"}}},
#           "top.middle.nested.[2]"
#       )
#       >> 'l'
#
class MyModule(sys.modules[__name__].__class__):
    def __call__(self, *args, **kwargs):  # module callable
        return pyoq(*args, **kwargs)


sys.modules[__name__].__class__ = MyModule


__all__ = ("pyoq",)
