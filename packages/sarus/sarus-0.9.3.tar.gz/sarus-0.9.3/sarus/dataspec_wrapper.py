from __future__ import annotations

import inspect
import logging
import re
import traceback
from typing import (
    Any,
    Dict,
    Generic,
    List,
    Literal,
    Optional,
    Tuple,
    TypeVar,
    Union,
    cast,
    get_args,
)

import sarus_data_spec.protobuf as sp
import sarus_data_spec.typing as st
from sarus_data_spec.context import global_context
from sarus_data_spec.dataspec_validator.typing import DataspecPrivacyPolicy
from sarus_data_spec.status import DataSpecErrorStatus
from sarus_data_spec.transform import variable

import sarus.manager.dataspec_api as api
from sarus.context.typing import LocalSDKContext
from sarus.manager.typing import SDKManager
from sarus.typing import DataSpecVariant, SyncPolicy
from sarus.utils import register_ops

try:
    from IPython.core.display import HTML
except ModuleNotFoundError:
    pass

logger = logging.getLogger(__name__)


IGNORE_WARNING = [
    "_ipython_canary_method_should_not_exist_",
    "_repr_png_",
]

T = TypeVar("T")


def class_name(_class: type) -> str:
    return getattr(_class, "__name__", str(_class))


class MetaWrapper(type):
    """Metaclass to delegate some class attributes to the wrapped class."""

    _wrapper_classes: List[Tuple[str, type]] = []

    def __new__(cls, name, bases, dct):
        """Creation of a new DataSpecWrapper class.

        The arguments `name`, `bases` and `dct` are the standard arguments
        passed to the `type` function when creating a new class
        https://docs.python.org/3/library/functions.html#type
        """
        new_wrapper_class = super().__new__(cls, name, bases, dct)

        if name != "DataSpecWrapper":
            # Set the wrapped class from the type annotation
            wrapped_python_class = get_args(
                new_wrapper_class.__orig_bases__[0]
            )[0]
            new_wrapper_class.__wraps__ = wrapped_python_class

            # Register the new class in the wrapper factory
            python_classname = str(wrapped_python_class)
            if python_classname == "~T":
                logger.warning(
                    f"Wrapper class {name} has no associated Python type."
                )
            else:
                MetaWrapper._wrapper_classes.append(
                    (str(wrapped_python_class), new_wrapper_class)
                )

        return new_wrapper_class

    def __getattr__(self, name):
        return getattr(self.__wraps__, name)


class DataSpecWrapper(Generic[T], metaclass=MetaWrapper):
    """This class wraps Sarus DataSpecs objects for the SDK.

    More specifically, it wraps 3 variants of the same DataSpec. These variants
    can be identified with the DataSpecVariant enum:
    - USER_DEFINED: the DataSpec as defined by the user
    - SYNTHETIC: the synthetic variant of the USER_DEFINED DataSpec
    - MOCK: a small sample of the SYNTHETIC variant

    The wrapper has a fallback behavior implemented in the __getattr__ method.
    Any attribute access attempt that is not explicitly catched by a method
    will be delegated to the SYNTHETIC dataspec's value.

    Subclasses such as sarus.pandas.DataFrame must implement the `value` method.
    """

    # This is a class variable hoding all DataSpecWrapper instances
    # This is used by the `dataspec_wrapper_symbols` method.
    instances: Dict[str, Tuple[int, str]] = dict()

    @classmethod
    def from_dataspec(
        cls, dataspec: st.DataSpec
    ) -> DataSpecWrapper(Generic[T]):
        """Instantiate a DataspecWrapper from a dataspec.

        We don't use the __init__ method because the __new__ method may be
        overwritten by the `sarus.utils.init_wrapped` decorator.
        """
        wrapper = object.__new__(cls)
        wrapper._set_dataspec(dataspec)
        return wrapper

    @classmethod
    def from_value(cls, value: T) -> DataSpecWrapper(Generic[T]):
        """Construct a DataSpecWrapper by wrapping a Python value."""
        return cls(value)

    def _set_dataspec(self, dataspec: st.DataSpec) -> None:
        self._dataspec = dataspec
        self._alt_dataspec = None
        self._alt_policy = None  # The alternative Dataspec's privacy policy
        self._traced_transform = None

        # This class only works with a LocalSDKContext
        context: LocalSDKContext = global_context()
        assert isinstance(context, LocalSDKContext)
        self._manager = context.manager()
        if context.sync_policy() == SyncPolicy.SEND_ON_INIT:
            self.alternative_dataspec(launch=True)
        # for .dot() to work add a else condition with self.alternative_dataspec()

        # Register wrapper instance
        DataSpecWrapper.instances[dataspec.uuid()] = id(self), class_name(
            self.__wraps__
        )

    def _set_variable(self, name: str, position: int):
        """Used to trace callables."""
        self._traced_transform = variable(name=name, position=position)

    def traced_transform(self) -> Optional[st.Transform]:
        """Return the wrapper's composed transform or variable when tracing."""
        return self._traced_transform

    def _set_traced_transform(
        self, traced_transform: Optional[st.Transform]
    ) -> None:
        self._traced_transform = traced_transform

    def manager(self) -> SDKManager:
        return self._manager

    def python_type(self) -> Optional[str]:
        """Return the value's Python type name.

        The SDKManager registers an attribute holding the MOCK value's
        Python type (see `SDKManager.infer_output_type` method). This is
        used to instantiate the right DataSpecWrapper class e.g. instantiate a
        sarus.pandas.DataFrame if the Python value is a pandas.DataFrame.
        """
        return self.manager().python_type(self._dataspec)

    def dataspec_wrapper_symbols(
        self, f_locals, f_globals
    ) -> Dict[str, Optional[str]]:
        """Returns the symbols table in the caller's namespace.

        For instance, if the data practitioner defines a DataSpecWrapper using
        the symbol X in his code (e.g. X = dataset.as_pandas()) then the symbol
        table contain the mapping between the DataSpecWrapper instances' ids
        and their symbols. This is used to make the dot representation more
        readable.
        """

        def is_ipython_variable(name: str) -> bool:
            return bool(re.search(r"^_\d+$", name))

        mapping = {
            id(obj): (name, class_name(obj.__wraps__))
            for name, obj in f_locals.items()
            if isinstance(obj, DataSpecWrapper)
            and not is_ipython_variable(name)
        }
        mapping.update(
            {
                id(obj): (name, class_name(obj.__wraps__))
                for name, obj in f_globals.items()
                if isinstance(obj, DataSpecWrapper)
                and not is_ipython_variable(name)
            }
        )
        names = dict()
        storage = self.manager().storage()
        rewriter = self.manager().dataspec_rewriter()
        for uuid, (_id, _class) in DataSpecWrapper.instances.items():
            ds = storage.referrable(uuid)
            info = mapping[_id] if _id in mapping else ("", _class)
            names[uuid] = info
            # The symbol & class is also valid for all variants
            for variant in rewriter.variants(ds):
                names[variant.uuid()] = info
        return names

    def dot(
        self,
        kind: Union[
            DataSpecVariant,
            Literal["rewritten", "mock", "original", "synthetic"],
        ] = "rewritten",
        remote: bool = True,
    ) -> str:
        """Graphviz's dot representation of the DataSpecWrapper graph.

        Uses color codes to show statuses.

        Args:
            kind (DataSpecVariant): the DataSpec to represent.
            remote (true): Which Manager to inspect.
                If true shows the DataSpec's status on the server,
                else show the DataSpec's status locally.
        """
        if isinstance(kind, str):
            kind = DataSpecVariant(kind)
        _, policy = self.alternative_dataspec()  # send to the server
        ds = self.dataspec(kind)
        if kind != DataSpecVariant.ALTERNATIVE:
            policy = None

        # pull attributes linking the variants
        api.pull_dataspec_graph(self.manager().client(), self._dataspec.uuid())

        caller_frame = inspect.currentframe().f_back
        symbols = self.dataspec_wrapper_symbols(
            caller_frame.f_locals, caller_frame.f_globals
        )
        return self.manager().dot(
            ds, symbols=symbols, remote=remote, policy=policy
        )

    def alternative_dataspec(
        self,
        target_epsilon: Optional[float] = None,
        launch: bool = False,
    ) -> Tuple[st.DataSpec, DataspecPrivacyPolicy]:
        """Send the DataSpec to the server for rewriting.

        The server sends an alternative DataSpec back which is compliant with
        the privacy policy defined for the current user.

        Args:
            launch (bool): If true, tell the server to launch the computation.
            target_epsilon (float, optional): The target_epsilon to evaluate
                the dataspec.

        Returns:
            A tuple with the alternative dataspec and the corresponding privacy
            policy.
        """
        context: LocalSDKContext = global_context()
        dataspec = self.dataspec(kind=DataSpecVariant.USER_DEFINED)

        if context.sync_policy() == SyncPolicy.MANUAL:
            # In MANUAL mode we evaluate on Synthetic data
            syn_ds = dataspec.variant(st.ConstraintKind.SYNTHETIC)
            return syn_ds, DataspecPrivacyPolicy.SYNTHETIC

        # Ask for a new rewriting
        if self._alt_dataspec is None or target_epsilon is not None:
            self.manager().push(dataspec)
            alt_dataspec, alt_policy = self.manager().rewrite(
                dataspec, target_epsilon
            )
            # Register the new dataspec as being represented by this wrapper
            DataSpecWrapper.instances[alt_dataspec.uuid()] = (
                id(self),
                class_name(self.__wraps__),
            )

            # Remember value for default epsilon
            if target_epsilon is None:
                self._alt_dataspec = alt_dataspec
                self._alt_policy = alt_policy
        else:
            # return already computed default alternative
            alt_dataspec = self._alt_dataspec
            alt_policy = self._alt_policy

        if launch:
            computation = self.manager().dataspec_computation(alt_dataspec)
            if self.manager().status(dataspec, computation.task_name) is None:
                self.manager().launch(alt_dataspec)

        return alt_dataspec, alt_policy

    def delete_from_local(self) -> None:
        """Delete a DataSpec from the local storage."""
        dataspec = self.dataspec(kind=DataSpecVariant.ALTERNATIVE)
        self.manager()._delete_local(dataspec.uuid())

    def __eval_policy__(self) -> str:
        """The alternative dataspec's privacy policy."""
        _, alt_policy = self.alternative_dataspec()
        return alt_policy.value

    def _status(self) -> Dict[str, Any]:
        dataspecs = {
            "user": self.dataspec(kind=DataSpecVariant.USER_DEFINED),
            "alt": self.dataspec(kind=DataSpecVariant.ALTERNATIVE),
            "mock": self.dataspec(kind=DataSpecVariant.MOCK),
        }

        result = {}
        for key, ds in dataspecs.items():
            statuses = self._manager._get_status(ds, remote=True)
            remote_status = [s for s in statuses if s["id"] == ds.uuid()][0]

            statuses = self._manager._get_status(ds, remote=False)
            local_status = [s for s in statuses if s["id"] == ds.uuid()][0]

            result[key] = {
                "remote": remote_status.get("code", "no_status"),
                "local": local_status.get("code", "no_status"),
            }

        return result

    def dataspec(
        self, kind: DataSpecVariant = DataSpecVariant.USER_DEFINED
    ) -> st.DataSpec:
        """Return one of the wrapped DataSpec object."""
        if kind == DataSpecVariant.USER_DEFINED:
            return self._dataspec
        if kind == DataSpecVariant.ALTERNATIVE:
            if self._alt_dataspec:
                return self._alt_dataspec
            else:
                return self._dataspec.variant(kind=st.ConstraintKind.SYNTHETIC)
        elif kind == DataSpecVariant.SYNTHETIC:
            return self._dataspec.variant(kind=st.ConstraintKind.SYNTHETIC)
        elif kind == DataSpecVariant.MOCK:
            return self._dataspec.variant(kind=st.ConstraintKind.MOCK)
        else:
            raise ValueError(f"Unknown kind {kind}")

    def save(self, path: str) -> None:
        """Save the representation of the sarus object to a file.

        Args:
            path (str): The path to save the object to.
        """
        self._manager._client.save(self, path)

    def __len__(self) -> int:
        logger.info(
            f"`__len__` not supported on {type(self)}, "
            "object has been evaluated for this method. "
            "See Sarus documentation."
        )
        return self.__sarus_eval__().__len__()

    def __repr__(self) -> int:
        return self.__sarus_eval__().__repr__()

    def __iter__(self) -> int:
        return self.__sarus_eval__().__iter__()

    def __float__(self) -> int:
        return self.__sarus_eval__().__float__()

    def __int__(self) -> int:
        return self.__sarus_eval__().__int__()

    def __bool__(self) -> int:
        return self.__sarus_eval__().__bool__()

    def __format__(self, *args, **kwargs) -> int:
        return self.__sarus_eval__().__format__(*args, **kwargs)

    def __sarus_eval__(
        self,
        target_epsilon: Optional[float] = None,
        verbose: Optional[int] = None,
    ) -> T:
        """Return the value of alternative DataSpec's variant."""
        alt_dataspec, alt_policy = self.alternative_dataspec(target_epsilon)
        if verbose is None:
            context: LocalSDKContext = global_context()
            verbose = context.verbose()

        if (
            target_epsilon is not None
            and target_epsilon > 0
            and alt_policy == DataspecPrivacyPolicy.SYNTHETIC
            and verbose >= 1
        ):
            logger.warning(
                "Warning: target_epsilon could not be consumed. "
                "This might be due to privacy budget "
                "constraints or some operations not "
                "rewritable with Differential Privacy."
            )

        if verbose >= 1:
            (
                has_transform,
                transform_to_small_data,
            ) = self.manager().has_transform(alt_dataspec, 'ToSmallData')
            if has_transform:
                to_small_data_size = (
                    transform_to_small_data.protobuf().spec.to_small_data.size
                )
                logger.warning(
                    "Due to the large size of the dataset, "
                    "the transforms were applied to a sample of the "
                    f"data only (sample_size={to_small_data_size}), "
                    "so your results may be affected.",
                    stacklevel=0,
                )

            message = alt_policy.value
            final_message = f"{message} (uuid:{self._dataspec.uuid()}, alt_uuid:{alt_dataspec.uuid()})"

            # check public result come from public table
            if alt_policy == DataspecPrivacyPolicy.PUBLIC:
                if any(
                    not source.is_transformed()
                    for source in alt_dataspec.sources()
                ):
                    print(final_message)
            else:
                if alt_policy == DataspecPrivacyPolicy.DP:
                    epsilon = self.manager().consumed_epsilon(alt_dataspec)
                    final_message = f"{message} (epsilon={epsilon:.2f}, uuid:{self._dataspec.uuid()}, alt_uuid:{alt_dataspec.uuid()})"

                print(final_message)

        if alt_dataspec.prototype() == sp.Dataset:
            dataset = cast(st.Dataset, alt_dataspec)
            value = dataset.to(self.__wraps__)
        else:
            scalar = cast(st.Scalar, alt_dataspec)
            value = cast(st.Scalar, scalar.value())

        return value

    def __getattr__(self, name: str) -> Any:
        """Called when trying to access an attribute of the DataSpecWrapper or calling a non-bound method.

        If this method is called, we have already passed by the default Python
        self.__getattribute__(name) and it found nothing.
        """
        if name not in IGNORE_WARNING:
            logger.info(
                f"`{name}` not supported on {type(self)}, "
                "object has been evaluated for this method. "
                "See Sarus documentation."
            )
            if self.traced_transform() is not None:
                raise NotImplementedError(
                    f"Cannot trace `{name}`. "
                    f"Not supported on type {self.__wraps__}"
                )
            return self.__sarus_eval__().__getattribute__(name)
        else:
            # IPython expects an error to be raised on some attributes.
            return object.__getattribute__(
                self, name
            )  # used to raise an error directly

    def _ipython_display_(self) -> None:
        try:
            display(self.__sarus_eval__())  # noqa: F821
        except Exception as e:
            if isinstance(e, DataSpecErrorStatus):
                display(e.extract_last_exc() or str(e))  # noqa: F821
            else:
                display(f"Exception: {e}")  # noqa: F821

            tb = traceback.format_exc()
            html_traceback = f"""
                <details>
                    <summary style="color: red;">Click to view traceback</summary>
                    <pre>{tb}</pre>
                </details>
                """
            display(HTML(html_traceback))  # noqa: F821

    def _mock_value(self) -> Any:
        """Debug purposes."""
        mock_ds = self.dataspec(DataSpecVariant.MOCK)
        if mock_ds.prototype() == sp.Dataset:
            return mock_ds.to_pandas()
        else:
            return mock_ds.value()


register_ops(use_parent_module=True)
