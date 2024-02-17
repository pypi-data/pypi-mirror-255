import inspect
import logging
import os
from datetime import date, datetime, time, timedelta, timezone
from functools import partial, wraps
from typing import Any, Callable, Dict, Optional, Type, Union

import numpy as np
import pandas as pd
import sarus_data_spec.protobuf as sp
import sarus_data_spec.typing as st
import yaml
from sarus_data_spec.context import global_context
from sarus_data_spec.status import DataSpecErrorStatus
from sarus_data_spec.transform import (
    external,
    error_estimation,
)
from sarus_data_spec.dataset import transformed

from .context.typing import LocalSDKContext
from .typing import (
    DataSpecVariant,
    DataSpecWrapper,
    FederatedWrapper,
    TracedFunction,
)

logger = logging.getLogger(__name__)

config_file = os.path.join(os.path.dirname(__file__), "config.yaml")
with open(config_file) as f:
    config = yaml.load(f.read(), Loader=yaml.Loader)


def module_config(module_name: str) -> Optional[Dict[str, Any]]:
    """Fetch the module's configuration from the config dict."""
    keys = module_name.split(".")
    module_conf = config
    for key in keys:
        if module_conf is None:
            return
        module_conf = module_conf.get(key)
    return module_conf


def eval(
    x: Any,
    target_epsilon: Optional[float] = None,
    verbose: Optional[int] = None,
) -> st.DataSpecValue:
    """Recursively evaluates DataSpecWrappers to values."""
    if isinstance(x, (DataSpecWrapper, FederatedWrapper)):
        return x.__sarus_eval__(target_epsilon, verbose)

    if target_epsilon is not None:
        logger.warning(
            "Ignoring `target_epsilon` since the evaluated object"
            " is not a Sarus object."
        )

    if isinstance(x, list):
        return [eval(x_) for x_ in x]
    elif isinstance(x, tuple):
        return tuple([eval(x_) for x_ in x])
    elif isinstance(x, dict):
        return {eval(k): eval(v) for k, v in x.items()}
    else:
        return x


def eval_perturbation(
    x: Any,
    target_epsilon: Optional[float] = None,
    verbose: Optional[int] = None,
) -> st.DataSpecValue:
    """Evaluates the error due to DP.

    To do so, compute an estimation of the 95th percentile of the absolute
    distance between the true value and DP values.
    If target_epsilon is None, defaults to the same as eval().
    """
    if isinstance(x, DataSpecWrapper):
        manager = x.manager()

        # Dataspec can be a Scalar or a Dataset. If a Dataset, it should be
        # convertible to a pd.Series.
        dataspec = x.dataspec()

        # needed to create new dataspecs with a different name
        # for the rewriter can associate a different seed
        dataspec_transform = dataspec.transform()
        dataspec_type = dataspec.prototype()
        args, kwargs = dataspec.parents()

        # get DP variants
        dp_dataspecs = []
        for i in range(19):
            # send to the server but don't evaluate the computational graph
            # to be sure to have always a different computational graph we
            # can add very small noise to the target epsilon.
            new_ds = transformed(
                dataspec_transform,
                *args,
                dataspec_type=sp.type_name(dataspec_type),
                dataspec_name=f"Perturbation_{i}",
                **kwargs,
            )
            manager.push(new_ds)
            dp_dataspec, _ = manager.rewrite(new_ds, target_epsilon)

            if i == 0 and not dp_dataspec.is_published():
                raise DataSpecErrorStatus(
                    (
                        False,
                        "The dataspec could not be rewritten in DP.",
                    )
                )
            dp_dataspecs.append(dp_dataspec)

        # normally the ErrorEstimation op is whitelisted
        dataspec = error_estimation()(dataspec, *dp_dataspecs)
        manager.push(dataspec)
        alt_dataspec, _ = manager.rewrite(dataspec)
        return alt_dataspec.value()

    if isinstance(x, list):
        # same as eval, but why don't we pass target_epsilon and verbose ?
        return [eval_perturbation(x_) for x_ in x]
    elif isinstance(x, tuple):
        return tuple([eval_perturbation(x_) for x_ in x])
    elif isinstance(x, dict):
        return {
            eval_perturbation(k): eval_perturbation(v) for k, v in x.items()
        }
    else:
        return x


def save(dw: DataSpecWrapper, path: str) -> None:
    """Save a DataSpecWrapper for loading in another notebook."""
    dw.sarus_save(path)


def is_standard_type_iterable(iterable) -> bool:
    """Checks if all elements in an iterable are instances of a specific set of standard types.

    This function is designed to quickly verify if a given iterable (such as list, set, tuple)
    contains only elements of certain standard types (like datetime, string, integer etc.).
    It provides a first faster alternative to checking each item individually for more complex
    types such as DataSpecWrapper or TracedFunction.

    Args:
        iterable (iterable): The iterable to check. This can be a list, set, tuple etc.

    Returns:
        bool: True if all elements in the iterable are of the specified types, False otherwise.
    """
    types = (
        pd.Timestamp,
        datetime,
        timedelta,
        timezone,
        time,
        date,
        np.generic,
        pd.Period,
        pd.Timedelta,
        pd.Interval,
        type,
        pd.api.extensions.ExtensionDtype,
        str,
        int,
        float,
        bool,
        type(None),
    )
    return all(isinstance(x, types) for x in iterable)


def convert_container(
    x: Union[DataSpecWrapper, Any]
) -> Union[DataSpecWrapper, Any]:
    """Recursively convert containers in DataSpecWrappers if one element is a DataSpecWrapper."""
    from sarus.std import Dict, List, Set, Slice, Tuple

    sarus_types = (DataSpecWrapper, TracedFunction)
    common_container_types = (list, set, tuple, dict, slice)
    iterable_container_types = (list, set, tuple)

    if isinstance(x, sarus_types):
        return x
    elif isinstance(x, common_container_types):
        # a first check that is faster than checking DataSpecWrapper or TracedFunction
        if isinstance(
            x, iterable_container_types
        ) and is_standard_type_iterable(x):
            return x

        if isinstance(x, list):
            elems = [convert_container(e) for e in x]
            if any(isinstance(e, sarus_types) for e in elems):
                return List(*elems)
            else:
                return x
        elif isinstance(x, set):
            elems = [convert_container(e) for e in x]
            if any(isinstance(e, sarus_types) for e in elems):
                return Set(*elems)
            else:
                return x
        elif isinstance(x, tuple):
            elems = [convert_container(e) for e in x]
            if any(isinstance(e, sarus_types) for e in elems):
                return Tuple(*elems)
            else:
                return x
        elif isinstance(x, dict):
            if is_standard_type_iterable(x.values()):
                return x

            elems = {k: convert_container(v) for k, v in x.items()}
            if any(isinstance(e, sarus_types) for e in elems.values()):
                return Dict(**elems)
            else:
                return x
        elif isinstance(x, slice):
            elems = [
                x.start,
                x.stop,
                x.step,
            ]
            if any([isinstance(e, sarus_types) for e in elems]):
                return Slice(*elems)
            else:
                return x
    else:
        return eval(x)


def eval_policy(x: Any) -> Optional[str]:
    """The alternative dataspec's privacy policy."""
    if isinstance(x, DataSpecWrapper):
        return x.__eval_policy__()
    else:
        return None


_registered_methods = []
_registered_functions = []


class register_method:
    """This decorator method allows to register methods declared in classes.

    It uses this behavior since Python 3.6
    https://docs.python.org/3/reference/datamodel.html#object.__set_name__
    """

    def __init__(
        self, method: Callable, code_name: str, use_parent_module: bool = False
    ) -> None:
        self.method = method
        self.code_name = code_name
        self.use_parent_module = use_parent_module

    def __set_name__(self, owner: Type, name: str) -> None:
        global _registered_methods
        module_name = owner.__module__
        if self.use_parent_module:
            doc_module_name = get_parent_module_name(module_name)
        else:
            doc_module_name = module_name
        _registered_methods.append(
            (
                doc_module_name,
                owner.__name__,
                name,
                self.code_name,
            )
        )
        setattr(owner, name, self.method)


def get_parent_module_name(module_name):
    return '.'.join(module_name.split('.')[:-1])


def register_ops(use_parent_module: bool = False):
    """Monkey-patching standard libraries to have Sarus functions.

    This functions is intended to be called in a Sarus module. The module's
    local variables will be modified dynamically (monkey patching) to replace
    some functions or methods by Sarus equivalent operations.

    Technically, we get the previous frame's (the module where the function is
    called) locals mapping and update it.

    The modified methods and functions are listed in the `sarus/config.yaml`
    file.
    """
    previous_frame = inspect.currentframe().f_back
    local_vars = previous_frame.f_locals
    module_name = local_vars["__name__"]
    module_conf = module_config(module_name)
    if module_conf is None:
        return
    # for documentation
    if use_parent_module:
        doc_module_name = get_parent_module_name(module_name)
    else:
        doc_module_name = module_name

    # Registering module functions
    global _registered_functions
    functions = module_conf.get("sarus_functions", {})
    for fn_name, fn_code_name in functions.items():
        local_vars[fn_name] = create_function(
            fn_code_name, module_name, fn_name, doc_module_name
        )

    # Registering explicit evaluation functions
    explicit_eval_fns = module_conf.get("explicit_eval", [])
    for fn_name in explicit_eval_fns:
        fn_obj = local_vars[fn_name]
        local_vars[fn_name] = explicit_sarus_eval(fn_obj)

    # Registering classes methods
    global _registered_methods
    classes = module_conf.get("classes", {})
    for class_name, methods in classes.items():
        class_obj = local_vars[class_name]
        for mth_name, mth_code_name in methods.items():
            setattr(
                class_obj,
                mth_name,
                create_method(
                    mth_code_name,
                    module_name,
                    class_name,
                    mth_name,
                    doc_module_name,
                ),
            )


def serialize_external(
    code_name: str,
    *args: Union[DataSpecWrapper, Any],
    **kwargs: Union[DataSpecWrapper, Any],
) -> st.DataSpec:
    """This function registers a new dataspec.

    Some arguments are instances of DataSpecWrapper and others are
    just Python object.
    """
    args = [convert_container(arg) for arg in args]
    kwargs = {
        eval(name): convert_container(arg) for name, arg in kwargs.items()
    }
    sarus_types = (DataSpecWrapper, TracedFunction)
    py_args = {
        i: arg
        for i, arg in enumerate(args)
        if not isinstance(arg, sarus_types)
    }
    ds_args_pos = [
        i for i, arg in enumerate(args) if isinstance(arg, sarus_types)
    ]
    ds_arg_types = {
        i: str(arg.__wraps__)
        if isinstance(arg, DataSpecWrapper)
        else "TracedFunction"
        for i, arg in enumerate(args)
        if isinstance(arg, sarus_types)
    }
    ds_args = [
        arg.dataspec(DataSpecVariant.USER_DEFINED)
        if isinstance(arg, DataSpecWrapper)
        else arg.transform()
        for arg in args
        if isinstance(arg, sarus_types)
    ]
    py_kwargs = {
        name: arg
        for name, arg in kwargs.items()
        if not isinstance(arg, sarus_types)
    }
    ds_kwargs = {
        name: arg.dataspec(DataSpecVariant.USER_DEFINED)
        if isinstance(arg, DataSpecWrapper)
        else arg.transform()
        for name, arg in kwargs.items()
        if isinstance(arg, sarus_types)
    }
    ds_kwargs_types = {
        name: str(arg.__wraps__)
        if isinstance(arg, DataSpecWrapper)
        else "TracedFunction"
        for name, arg in kwargs.items()
        if isinstance(arg, sarus_types)
    }
    transform = external(
        id=code_name,
        py_args=py_args,
        py_kwargs=py_kwargs,
        ds_args_pos=ds_args_pos,
        ds_types={**ds_arg_types, **ds_kwargs_types},
    )
    new_dataspec = transform(*ds_args, **ds_kwargs)

    # Compute the traced transform if tracing
    tr_args = [
        arg.traced_transform()
        for arg in args
        if isinstance(arg, DataSpecWrapper)
    ]
    tr_kwargs = {
        name: arg.traced_transform()
        for name, arg in kwargs.items()
        if isinstance(arg, DataSpecWrapper)
    }
    is_not_traced = [tr is None for tr in tr_args] + [
        tr is None for tr in tr_kwargs.values()
    ]
    if all(is_not_traced):
        traced_transform = None
    elif any(is_not_traced):
        raise ValueError("Some inputs are traced and other are not.")
    else:
        traced_transform = transform(*tr_args, **tr_kwargs)

    return new_dataspec, traced_transform


def _sarus_op(
    code_name: str,
    inplace: bool = False,
    register: bool = False,
    is_property: bool = False,
    use_parent_module: bool = False,
) -> Callable:
    """Parametrized decorator to register a Sarus external op."""

    def parametrized_wrapper(ops_fn: Callable) -> Callable:
        @wraps(ops_fn)
        def wrapper_fn(
            *args: Union[DataSpecWrapper, Any],
            **kwargs: Union[DataSpecWrapper, Any],
        ) -> DataSpecWrapper:
            new_dataspec, traced_transform = serialize_external(
                code_name, *args, **kwargs
            )
            context: LocalSDKContext = global_context()

            new_dataspec_wrapper = context.wrapper_factory().create(
                new_dataspec
            )
            if isinstance(new_dataspec_wrapper, DataSpecWrapper):
                new_dataspec_wrapper._set_traced_transform(traced_transform)

            if inplace:
                self: DataSpecWrapper = args[0]  # TODO check semantic
                self._set_dataspec(new_dataspec)
                if isinstance(self, DataSpecWrapper):
                    self._set_traced_transform(traced_transform)

            return new_dataspec_wrapper

        if is_property:
            wrapper_fn = property(wrapper_fn)

        if register:
            wrapper_fn = register_method(
                wrapper_fn, code_name, use_parent_module=use_parent_module
            )

        return wrapper_fn

    return parametrized_wrapper


sarus_method = partial(_sarus_op, register=True, is_property=False)
sarus_property = partial(_sarus_op, register=True, is_property=True)


def sarus_custom_method(code_name: str) -> Callable:
    """Decorator to simply register the method in the documentation.

    The the implementation details are left to the SDK.
    """

    def parametrized_wrapper(method: Callable) -> Callable:
        return register_method(method, code_name)

    return parametrized_wrapper


def sarus_init(code_name: str, use_parent_module: str = False) -> Callable:
    """Decorator to initialize DataSpecWrapper classes from ops."""

    def parametrized_wrapper(ops_fn: Callable) -> Callable:
        @wraps(ops_fn)
        def init_fn(
            self: DataSpecWrapper,
            *args: Union[DataSpecWrapper, Any],
            **kwargs: Union[DataSpecWrapper, Any],
        ) -> None:
            new_dataspec, traced_transform = serialize_external(
                code_name, *args, **kwargs
            )
            self._set_dataspec(new_dataspec)
            self._set_traced_transform(traced_transform)

        init_fn = register_method(
            init_fn, code_name, use_parent_module=use_parent_module
        )

        return init_fn

    return parametrized_wrapper


def create_function(
    code_name: str,
    module_name: str,
    fn_name: str,
    doc_module_name: str = None,
    inplace: bool = False,
) -> Callable:
    """Create an op and register it as a function in a module."""
    global _registered_functions
    if doc_module_name is None:
        doc_module_name = module_name
    _registered_functions.append((doc_module_name, fn_name, code_name))

    @_sarus_op(code_name=code_name, inplace=inplace)
    def dummy_fn(*args, **kwargs):
        ...

    return dummy_fn


def create_method(
    code_name: str,
    module_name: str,
    class_name: str,
    method_name: str,
    doc_module_name: str = None,
    inplace: bool = False,
) -> Callable:
    """Create an op and register it as a method of a class."""
    global _registered_methods
    if doc_module_name is None:
        doc_module_name = module_name
    _registered_methods.append(
        (doc_module_name, class_name, method_name, code_name)
    )

    @_sarus_op(code_name=code_name, inplace=inplace)
    def dummy_fn(*args, **kwargs):
        ...

    return dummy_fn


def create_lambda_op(code_name: str, inplace: bool = False) -> Callable:
    """Create an op and do not register it."""

    @_sarus_op(code_name=code_name, inplace=inplace)
    def dummy_fn(*args, **kwargs):
        ...

    return dummy_fn


@_sarus_op(code_name="std.LEN")
def length(__o: object):
    ...


@_sarus_op(code_name="std.INT")
def integer(__o: object):
    ...


@_sarus_op(code_name="std.FLOAT")
def floating(__o: object):
    ...


def explicit_sarus_eval(func):
    """Decorator to explicitly collect Dataspec's values before calling."""

    @wraps(func)
    def wrapped_func(*args, **kwargs):
        args = [eval(arg) for arg in args]
        kwargs = {key: eval(val) for key, val in kwargs.items()}
        return func(*args, **kwargs)

    return wrapped_func


def init_wrapped(wrapper_class):
    """Define the constructor to return a wrapped instance."""
    assert issubclass(wrapper_class, DataSpecWrapper)

    def __new__(cls, *args, **kwargs):
        return wrapper_class.__wraps__(*args, **kwargs)

    wrapper_class.__new__ = staticmethod(__new__)

    return wrapper_class
