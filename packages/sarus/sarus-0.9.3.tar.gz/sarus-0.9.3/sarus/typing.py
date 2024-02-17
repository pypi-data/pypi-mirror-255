from enum import Enum
from typing import (
    Any,
    Callable,
    Dict,
    Iterator,
    Optional,
    Protocol,
    Type,
    TypeVar,
    Union,
    runtime_checkable,
)

import sarus_data_spec.context.typing as sct
import sarus_data_spec.typing as st
from requests import Session


class SyncPolicy(Enum):
    MANUAL = 0
    SEND_ON_INIT = 1
    SEND_ON_VALUE = 2


class DataSpecVariant(Enum):
    USER_DEFINED = "original"
    SYNTHETIC = "synthetic"
    MOCK = "mock"
    ALTERNATIVE = "rewritten"


T = TypeVar("T")

# to avoid infinite loops
SPECIAL_WRAPPER_ATTRIBUTES = [
    "_alt_dataspec",
    "_dataspec",
    "_alt_policy",
    "_traced_transform",
    "_manager",
    "__sarus_idx__",
]

MOCK = "mock"
PYTHON_TYPE = "python_type"
ADMIN_DS = "admin_ds"
ATTRIBUTES_DS = "attributes_ds"


@runtime_checkable
class DataSpecWrapper(Protocol[T]):
    def python_type(self) -> Optional[str]:
        ...

    def dataspec(
        self, kind: DataSpecVariant = DataSpecVariant.USER_DEFINED
    ) -> st.DataSpec:
        ...

    def __sarus_eval__(
        self,
        target_epsilon: Optional[float] = None,
        verbose: Optional[int] = None,
    ) -> st.DataSpecValue:
        """Return value of synthetic variant."""
        ...

    def traced_transform(self) -> Optional[st.Transform]:
        ...

    def _set_traced_transform(
        self, traced_transform: Optional[st.Transform]
    ) -> None:
        ...

    def _set_dataspec(self, dataspec: st.DataSpec) -> None:
        ...

    def _set_variable(self, name: str, position: int):
        ...


@runtime_checkable
class TracedFunction(Protocol):
    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        ...

    def transform(self) -> st.Transform:
        ...


class DataSpecWrapperFactory(Protocol):
    def register(
        self,
        python_classname: str,
        sarus_wrapper_class: DataSpecWrapper,
    ) -> None:
        ...

    def create(self, dataspec: st.DataSpec) -> Union[DataSpecWrapper, Any]:
        """Create a wrapper class from a DataSpec.

        If the dataspec's python value is not managed by the SDK, returns an
        unwrapped Python object.
        """

    def from_value(self, value: Any) -> DataSpecWrapper:
        ...

    def registry(self) -> Dict[str, Type[DataSpecWrapper]]:
        ...


class Client:
    def url(self) -> str:
        """Return the URL of the Sarus server."""

    def session(self) -> Session:
        """Return the connection to the server."""

    def context(self) -> sct.Context:
        """Return the client's context."""


@runtime_checkable
class FederatedWrapper(Protocol[T]):
    def __map_wrappers__(self, fun: Callable[[T], Any]) -> Iterator[Any]:
        """Safe iteration over the federated DataSpecWrappers."""
        ...

    def __federated_eval__(self, fun: Callable[[T], Any]) -> Any:
        """__federated_eval__ has the signature: ((W1,..,Wn),f) -> (f(W1),..,f(Wn))."""
        ...

    def __sarus_eval__(
        self,
        target_epsilon: Optional[float] = None,
        verbose: Optional[int] = None,
    ) -> st.DataSpecValue:
        """Return value of synthetic variant."""
        ...
