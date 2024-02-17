import typing as t

import sarus_data_spec.status as stt
from sarus_data_spec import typing as st
from sarus_data_spec.constants import SCALAR_TASK

from sarus.manager.base_remote import RemoteComputation

from .dataspec_api import dataspec_status, launch_dataspec, scalar_result


class ValueComputationOnServer(RemoteComputation[t.Any]):
    """ValueComputation on the Sarus server through the REST API."""

    task_name = SCALAR_TASK

    def launch_task(self, dataspec: st.DataSpec) -> None:
        """Launch the computation of a Scalar on the server."""
        status = self.status(dataspec=dataspec)
        if status is None:
            launch_dataspec(self.computing_manager().client(), dataspec.uuid())

    async def result_from_stage_properties(
        self,
        dataspec: st.DataSpec,
        properties: t.Mapping[str, str],
        **kwargs: t.Any,
    ) -> t.Any:
        scalar = t.cast(st.Scalar, dataspec)

        # We do not download weights on sarus.eval for LLM
        if scalar.is_pretrained_model() or scalar.is_fitted_model():
            return None

        return scalar_result(
            self.computing_manager().client(), dataspec.uuid()
        )

    def status(self, dataspec: st.DataSpec) -> t.Optional[st.Status]:
        """Retreive the status from the server.

        In this case, the computation retrieves the status from the server
        via an API call, a local status is created but not stored in order
        to use it just for the pollin
        """
        status_proto = dataspec_status(
            client=self.computing_manager().client(),
            uuid=dataspec.uuid(),
            task_names=[self.task_name],
        )
        if status_proto is None:
            return None
        else:
            return stt.Status(protobuf=status_proto, store=False)
