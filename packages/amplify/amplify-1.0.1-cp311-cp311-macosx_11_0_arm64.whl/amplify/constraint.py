import warnings

from typing_extensions import deprecated

from . import Constraint
from . import clamp as _clamp
from . import equal_to as _equal_to
from . import greater_equal as _greater_equal
from . import less_equal as _less_equal
from . import one_hot as _one_hot
from ._backward import InequalityFormulation, _deprecation_warnings_msg

warnings.warn(
    _deprecation_warnings_msg(f"{__name__} module", "amplify without submodule"), DeprecationWarning, stacklevel=2
)

__all__ = ["equal_to", "one_hot", "less_equal", "greater_equal", "clamp", "penalty"]


@deprecated(_deprecation_warnings_msg("amplify.constraint.equal_to", "amplify.equal_to"))
def equal_to(*args, **kwargs):
    """alias of :func:`~amplify.equal_to`"""
    return _equal_to(*args, **kwargs)


@deprecated(_deprecation_warnings_msg("amplify.constraint.one_hot", "amplify.one_hot"))
def one_hot(*args, **kwargs):
    """alias of :func:`~amplify.one_hot`"""
    return _one_hot(*args, **kwargs)


@deprecated(_deprecation_warnings_msg("amplify.constraint.less_equal", "amplify.less_equal"))
def less_equal(poly, le, label="", method=InequalityFormulation.Default):
    """alias of :func:`~amplify.less_equal`"""
    return _less_equal(poly, le, label, method.value)


@deprecated(_deprecation_warnings_msg("amplify.constraint.greater_equal", "amplify.greater_equal"))
def greater_equal(poly, le, label="", method=InequalityFormulation.Default):
    """alias of :func:`~amplify.greater_equal`"""
    return _greater_equal(poly, le, label, method.value)


@deprecated(_deprecation_warnings_msg("amplify.constraint.clamp", "amplify.clamp"))
def clamp(poly, ge, le, label="", method=InequalityFormulation.Default):
    """alias of :func:`~amplify.clamp`"""
    return _clamp(poly, (ge, le), label, method.value)


@deprecated(_deprecation_warnings_msg("amplify.constraint.penalty", "amplify.Constraint"))
def penalty(poly, eq=None, le=None, ge=None, label=""):
    """alias of constructor of :class:`~amplify.Constraint`"""
    if eq is not None:
        return Constraint(poly, eq=eq, penalty=poly, label=label)
    if le is not None:
        return Constraint(poly, le=le, penalty=poly, label=label)
    if ge is not None:
        warnings.warn(
            "Using the keyword argument `ge` on `penalty` function will cause an unintended result. \n"
            "Use penalty(-f, le=-t) instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return Constraint(poly, ge=ge, penalty=poly, label=label)

    return Constraint(poly, eq=0, penalty=poly, label=label)
