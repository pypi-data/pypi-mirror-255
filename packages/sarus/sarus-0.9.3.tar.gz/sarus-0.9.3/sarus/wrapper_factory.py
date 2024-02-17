from typing import Any, Dict, Type, Union, cast

import sarus_data_spec.protobuf as sp
import sarus_data_spec.typing as st
from sarus_data_spec.context import global_context

from sarus.dataspec_wrapper import DataSpecWrapper
from sarus.manager.typing import SDKManager
from sarus.utils import convert_container


class DataSpecWrapperFactory:
    def __init__(self):
        self._registry = {}

    def register(
        self,
        python_classname: str,
        sarus_wrapper_class: Type[DataSpecWrapper],
    ) -> None:
        self._registry[python_classname] = sarus_wrapper_class

    def create(self, dataspec: st.DataSpec) -> Union[DataSpecWrapper, Any]:
        """Create a wrapper class from a DataSpec.

        If the dataspec's python value is not managed by the SDK, returns an
        unwrapped Python object.
        """
        context = global_context()
        manager: SDKManager = context.manager()
        python_type = manager.python_type(dataspec)
        SarusWrapperClass = self._registry.get(python_type)
        if SarusWrapperClass:
            return SarusWrapperClass.from_dataspec(dataspec)
        else:
            # Datasets are either pd.DataFrame or pd.Series
            if dataspec.prototype() != sp.Scalar:
                raise TypeError(f"Expected a Scalar {dataspec}")
            scalar = cast(st.Scalar, dataspec)
            alt_scalar = scalar.variant(
                kind=st.ConstraintKind.SYNTHETIC, public_context=[]
            )
            return alt_scalar.value()

    def from_value(self, value: Any) -> DataSpecWrapper:
        """Creates a wrapper class from a Python object.

        The Python object can be a container, in which wase it might contain a
        DataSpecWrapper nested deeper. Such containers will be converted to
        DataSpecWrappers.
        """
        value = convert_container(value)
        if isinstance(value, DataSpecWrapper):
            return value

        python_type = str(type(value))
        SarusWrapperClass = self.registry().get(python_type)
        if SarusWrapperClass is None:
            raise TypeError(
                f"Cannot convert type {python_type} to DataSpecWrapper."
            )

        return SarusWrapperClass.from_value(value)

    def registry(self) -> Dict[str, Type[DataSpecWrapper]]:
        return self._registry
