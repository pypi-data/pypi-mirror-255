from __future__ import annotations

import inspect
import typing as t
from functools import wraps

import sarus_data_spec.typing as st
from sarus_data_spec.context import global_context

from sarus.context.typing import LocalSDKContext
from sarus.dataspec_wrapper import DataSpecWrapper
from sarus.utils import convert_container


def trace(
    python_callable: t.Callable[..., t.Any]
) -> t.Callable[..., TracedFunction]:
    """Serialize a python callable into a Transform.

    The transform can then be safely executed on the server.

    The syntax would be `traced_function = trace(preprocess)(example_data)`
    similar to Jax's jit.
    """

    @wraps(python_callable)
    def tracing_fn(
        *args: DataSpecWrapper, **kwargs: DataSpecWrapper
    ) -> TracedFunction:
        # Make tracing copies of the input arguments
        tracing_args = []
        tracing_kwargs = {}
        args_names = [
            param for param in inspect.signature(python_callable).parameters
        ]
        context: LocalSDKContext = global_context()
        for i, arg in enumerate(args):
            if not isinstance(arg, DataSpecWrapper):
                arg = context.wrapper_factory().from_value(arg)
            tracing_arg = type(arg).from_dataspec(arg._dataspec)
            # enable tracing mode
            tracing_arg._set_variable(name=args_names[i], position=i)
            tracing_args.append(tracing_arg)

        for name, arg in kwargs.items():
            if not isinstance(arg, DataSpecWrapper):
                arg = context.wrapper_factory().from_value(arg)
            tracing_arg = type(arg).from_dataspec(arg._dataspec)
            # enable tracing mode
            tracing_arg._set_variable(
                name=name, position=args_names.index(name)
            )
            tracing_kwargs[name] = tracing_arg

        # Call the user-defined callable with the tracing arguments
        traced_result = python_callable(*tracing_args, **tracing_kwargs)
        traced_result = convert_container(traced_result)

        # Check that the result is indeed traced
        if not isinstance(traced_result, DataSpecWrapper):
            raise TypeError(
                "Error while serializing: the traced "
                "result is not a DataSpecWrapper."
            )

        traced_transform = traced_result.traced_transform()
        if traced_transform is None:
            raise ValueError(
                "Error while serializing: the traced transform is None."
            )

        return TracedFunction(traced_transform)

    return tracing_fn


class TracedFunction:
    def __init__(self, transform: st.Transform) -> None:
        self._transform = transform
        self._callable = transform.composed_callable()

    def __call__(self, *args: t.Any, **kwargs: t.Any) -> t.Any:
        return self._callable(*args, **kwargs)

    def transform(self) -> st.Transform:
        return self._transform

    def dot(self) -> str:
        return self._transform.dot()
