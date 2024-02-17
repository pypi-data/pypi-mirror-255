"""Copyright 2023 Sarus SAS.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Sarus library to leverage sensitive data without revealing them.

This lib contains classes and method to federate different Sarus objects
to process them simultaneously.
"""
from __future__ import annotations

import logging
import types
import typing as t

import sarus
from sarus import Dataset
from sarus.context.typing import LocalSDKContext
from sarus.dataspec_wrapper import DataSpecWrapper
from sarus.pandas.dataframe import DataFrame

SILENCED_IPYTHON_METHODS = [
    "_ipython_canary_method_should_not_exist_",
    "_ipython_display_",
    "_repr_mimebundle_",
    "_repr_html_",
    "_repr_markdown_",
    "_repr_svg_",
    "_repr_png_",
    "_repr_pdf_",
    "_repr_jpeg_",
    "_repr_latex_",
    "_repr_json_",
    "_repr_javascript_",
]

T = t.TypeVar("T")
W = t.TypeVar("W", bound=DataSpecWrapper, covariant=True)


CMP_INTERFACE = {
    "__ge__",
    "__gt__",
    "__le__",
    "__lt__",
    "__ne__",
}


def get_interface(obj: t.Any, parent: t.Any = object) -> t.Set[str]:
    x, y = map(set, map(dir, (obj, parent)))
    return (x - y - {"__dict__"}) | (CMP_INTERFACE & y)


def federated_functor(name) -> t.Callable:
    """Functor to automatically vectorize a method.

    It maps a method from the base class based on its name to a vectorized
    function to be used as a method.

    We have the diagram:

    Vec[X]------------------>Vec[Y]
      |           F            ^
      |                        |
      |federate⁻¹     federate |
      |                        |
      v           f            |
      X----------------------->Y

    TODO: vectorizing functions in general; the output is then the following:
      (⨂f)(U) -> ⨂(f(U)) ~ (f1(U),...,fn(U)).
    More generally, we currently lack the tools to define:
      - (⨂f)(⨂U) -> ⨂(f(U)) ~ (f1(U1),...,fn(Un))
      - f⨂: f -> ((⨂U,V) -> ⨂(f(U,V))) ~ (f(U1,V),...,f(Un,V))
      - f⨂: f -> ((⨂U,⨂V) -> ⨂(f(U,V))) ~ (f(U1,V1),...,f(Un,Vn))
    which requires analyzing args and kwargs, and adding implementations
    for Python builtins.

    TODO: it lacks the support for aligning Federated parameters.
    This means that we have:
      federate([1, 2]) < 1.5 == federate([1 < 1.5, 2 < 1.5])
                             == federate([False, True])
    but we do not have:
      federate([1, 2]) < federate([0, 4]) == federate([1 < 0, 2 < 4])
                                          == federate([False, True])
    Instead we have: NotImplemented.
    NB: `==` is not working for that very same reason !
    """

    def f(self, *args, **kwargs):
        return federate(
            [
                m(*args, **kwargs)
                for m in (getattr(item, name) for item in self.__items__)
            ]
        )

    f.__name__ = name
    return f


def clone_interface(
    federating_class: t.Type,
    federated_class: t.Type,
    base_class: t.Type = object,
) -> None:
    """Adds to the Federating class the methods of the federated.

    This modifies the Federating class in-place.
    Some methods such as `__lt__` and such have to be defined at the
    class-level for some synthetic mechanisms to work, so we cannot rely
    exclusively on `getattr`.

    TODO: a better cloning of properties/descriptors
    see: https://docs.python.org/3/library/inspect.html#inspect.getattr_static
    Currently, properties depend on the getattr implementation
    They could be defined with the dct of the MetaClass and `property(method)`
    but for extensive coverage the issue of the setter and deleter are to
    be investigated as well.
    """
    federating_class.__wrapper_interface__ = get_interface(
        federated_class, base_class
    )
    for name in federating_class.__wrapper_interface__:
        try:
            m = getattr(federated_class, name)
            is_callable = callable(m)
        except Exception:
            is_callable = False

        method = federated_functor(name)
        if is_callable:
            setattr(federating_class, name, method)


class FederatedMeta(type):
    """Metaclass to federate any kind of objects."""

    __federated_instances__: t.Dict[t.Type, t.Type] = {}

    def __new__(cls, name, bases, dct):
        """Creation of a new Federated class."""
        orig_bases = dct["__orig_bases__"]
        federated_class = t.get_args(orig_bases[0])[0]

        new_federating_class = super().__new__(cls, name, bases, dct)
        new_federating_class.__python_type__ = federated_class
        if isinstance(federated_class, type):
            if federated_class in FederatedMeta.__federated_instances__:
                return FederatedMeta.__federated_instances__[federated_class]
            elif issubclass(federated_class, DataSpecWrapper):
                """
                # clone_interface(
                #     new_federating_class, federated_class, DataSpecWrapper
                # )
                # the default behavior of federated wrappers is a fallback to
                # the first element, which is implemented in its `getattr`
                # only **implemented** methods can be vectorized
                """
                pass
            else:
                clone_interface(new_federating_class, federated_class)
            FederatedMeta.__federated_instances__[
                federated_class
            ] = new_federating_class
        return new_federating_class


class Vectorized(t.Generic[T], metaclass=FederatedMeta):
    """Base class for federated analytics.

    This class groups calls to a list of objects in a duck-typing way.
    We write ⨂P = (P1,...,Pn) our federated collection with n partitions in the docs.
    """

    def __init__(self, items: t.List[T]) -> None:
        self.__items__: t.List[T] = list(items)

    def __repr__(self) -> str:
        items = "\n".join(f"  - {item}" for item in self.__items__)
        return f"{type(self).__name__}:\n{items}"

    def __str_(self) -> str:
        return repr(self)

    def __getattr__(self, name) -> Vectorized:
        """Default behavior is to return a Federate object with the output.

        The output of this function verifies (⨂P).f == ⨂(P.f) ~ (P1.f,...,Pn.f)
        """
        return federate([getattr(item, name) for item in self.__items__])


class WithContext(t.Generic[T]):
    """Minimal wrap to keep safety of execution.

    Any output of the default behavior of FederatedWrapper is wrapped with it,
    so that call is run through the correct context.

    The output can be a method, a closure with a dataspec, a property, so we
    must cover many situation. The solution here is to always return a
    WithContext object.

    TODO: better knowledge of class cloning to only protect known class
    attributes, methods and properties, using a Metaclass.
    """

    def __init__(
        self,
        wrapper: DataSpecWrapper,
        context: t.Optional[LocalSDKContext] = None,
    ) -> None:
        self.context = (
            context if context is not None else wrapper.dataspec().context()
        )
        self.wrapped = wrapper

    def __call__(self, *args, **kwargs) -> t.Any:
        with self.context:
            res = self.wrapped(*args, **kwargs)
        return WithContext(res, self.context)

    def __getattr__(self, name: str) -> t.Any:
        with self.context:
            res = getattr(self.wrapped, name)
        return WithContext(res, self.context)


class FederatedWrapper(Vectorized[W]):
    """Base class for federated DataSpecWrappers.

    It handles the dataspec specifics to make the federated computations work.
    """

    def __map_wrappers__(
        self, fun: t.Callable[[W], t.Any]
    ) -> t.Iterator[t.Any]:
        """Main entry to operate on the DataspecWrappers.

        This iterator yields the output of the function applied to the datasets
        after ensuring the suitable context has been set.
        """
        for item in self.__items__:
            # this is  very permissive to let duck-typing work
            if isinstance(item, DataSpecWrapper):
                with item.dataspec().context():
                    res = fun(item)
            else:
                res = fun(item)
            yield res
        return

    def __federated_eval__(
        self, fun: t.Callable[[W], t.Any]
    ) -> Vectorized[t.Any]:
        """Helper function to apply the function.

        __federated_eval__ has the signature: (⨂W,f) -> ⨂(f(W)) ~ (f(W1),...,f(Wn))
        """
        return federate(list(self.__map_wrappers__(fun)))

    def __sarus_eval__(
        self,
        target_epsilon: t.Optional[float] = None,
        verbose: t.Optional[int] = None,
    ) -> Vectorized[t.Any]:
        """Return a public value for the dataspec.

        We want sarus.eval(⨂W) -> ⨂(sarus.eval(W))

        TODO: __sarus_eval__() means we are getting a result out of our system
        in a plain Python type (not boxed). So the result should probably be
        typed with `U` if `W < DataSpecWrapper[U]` which means we must perform
        reduces here.
        """
        return self.__federated_eval__(
            lambda w: sarus.eval(w, target_epsilon, verbose)
        )

    def __repr__(self) -> str:
        slugnames = ", ".join(
            self.__map_wrappers__(lambda w: w.dataspec()['slugname'])
        )
        return f"{type(self).__name__}({slugnames})"

    def __getattr__(self, name):
        """Default implementation for any op of a FederatedWrapper.

        The current implementation restricts this to: (⨂W).f -> W1.f
        that is: it returns the FederatedWrapper made of the op applied to the first partition.
        """
        if name not in SILENCED_IPYTHON_METHODS:
            logging.warning(
                f"Applying transformation to the first federated object only as '{name}' is not supported in federated version for now. Please tell your account manager if you need it."
            )
        first = next(self.__map_wrappers__(lambda w: getattr(w, name)))
        first_context = self.__items__[0].dataspec().context()
        return WithContext(first, first_context)


class FederatedDataset(FederatedWrapper[Dataset]):
    """A view of a federated dataset as an Arrow iterator."""

    def __init__(self, list_of_datasets: t.List[Dataset]) -> None:
        super().__init__(list_of_datasets)
        slugnames = repr(self)[:-1].replace("FederatedDataset(", "")
        logging.debug(
            f"The datasets {slugnames} have been added to the federated dataset."
        )

    def as_pandas(self) -> FederatedWrapper[sarus.pandas.DataFrame]:
        return self.__federated_eval__(lambda w: w.as_pandas())

    def __getitem__(self, item: t.List[str]) -> Dataset:
        return self.table(item)

    def table(self, table_name: t.List[str]) -> Dataset:
        return self.__federated_eval__(lambda w: w.table(table_name))


class FederatedDataframe(FederatedWrapper[DataFrame]):
    """A view of a federated dataset as a pandas DataFrame."""

    def __getitem__(self, column: str) -> FederatedDataframe:
        return self.__federated_eval__(lambda w: w.__getitem__(column))

    def count(self, *args, **kwargs) -> int:
        return sum(
            self.__federated_eval__(
                lambda w: w.count(*args, **kwargs)
            ).__items__
        )

    def sum(self, *args, **kwargs):
        return sum(
            self.__federated_eval__(lambda w: w.sum(*args, **kwargs)).__items__
        )

    def mean(self, *args, **kwargs):
        S = self.sum(*args, **kwargs)
        N = self.count(*args, **kwargs)
        return S / N[S.index]

    @property
    def shape(self):
        shapes = self.__federated_eval__(lambda w: w.shape).__items__
        return [sum(_[0] for _ in shapes), *shapes[0][1:]]


def federate(items: t.List[T]) -> Vectorized[T]:
    """Main entry function for federating objects.

    It can generate on-the-fly new classes to federate previously unseen
    objects, with a specific care when T < DataSpecWrapper.
    We built a Monad !
    """
    item_type = type(items[0])
    if item_type in FederatedMeta.__federated_instances__:
        return FederatedMeta.__federated_instances__[item_type](items)
    elif issubclass(item_type, DataSpecWrapper):
        federated_base = FederatedWrapper[item_type]
    else:
        federated_base = Vectorized[item_type]
    class_name = f"Federated{item_type.__name__.title()}"
    custom_class = types.new_class(class_name, (federated_base,), {})
    return custom_class(items)
