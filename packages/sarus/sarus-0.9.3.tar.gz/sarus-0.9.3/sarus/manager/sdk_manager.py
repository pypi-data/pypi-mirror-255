import json
import os
import tempfile
import typing as t
from collections import defaultdict

import pandas as pd
import pyarrow as pa
import sarus_data_spec.protobuf as sp
import sarus_data_spec.status as stt
import sarus_data_spec.storage.typing as storage_typing
import sarus_data_spec.typing as st
from sarus_data_spec.attribute import attach_properties
from sarus_data_spec.constants import (
    ARROW_TASK,
    BIG_DATA_TASK,
    IS_BIG_DATA,
    SCALAR_TASK,
)
from sarus_data_spec.dataspec_validator.privacy_limit import DeltaEpsilonLimit
from sarus_data_spec.dataspec_validator.typing import DataspecPrivacyPolicy
from sarus_data_spec.manager.base import Base
from sarus_data_spec.manager.computations.base import BaseComputation
from sarus_data_spec.manager.computations.local.schema import SchemaComputation
from sarus_data_spec.manager.ops.processor.routing import (
    TransformedDataset,
    TransformedScalar,
)
from sarus_data_spec.manager.ops.source.routing import SourceScalar

import sarus.manager.dataspec_api as api
from sarus.llm.pretrained import TrainState
from sarus.typing import ADMIN_DS, MOCK, PYTHON_TYPE, Client

from .arrow_local import ToArrowComputation
from .arrow_remote import ToArrowComputationOnServer
from .cache_scalar_local import CacheScalarComputation
from .parquet_local import ToParquetComputation
from .value_local import ValueComputation
from .value_remote import ValueComputationOnServer


class SDKManager(Base):
    """The Manager of the SDK running on the client side.

    This Manager has two additional functionalities compared to the
    DelegatingManager manager.

    First, it manages the relationship with the remote server using the API
    endpoints.

    Second, this Manager defines a MOCK version for every DataSpec. The MOCK is
    defined as a smaller version of a DataSpec. In practice, it is a sample of
    SYNTHETIC at the source and MOCKs of transformed DataSpecs are the
    transforms of the MOCKs.

    The MOCK is created and its value computed in the `infer_output_type`
    method. This serves two purposes. First, it provides immediate feedback to
    the user in case of erroneous computation. Second, it allows identifying the
    MOCK's value Python type which is then used by the SDK to instantiate the
    correct DataSpecWrapper type (e.g. instantiate a sarus.pandas.DataFrame if
    the value is a pandas.DataFrame).
    """

    def __init__(
        self,
        storage: storage_typing.Storage,
        protobuf: sp.Manager,
        client: Client,
    ) -> None:
        super().__init__(storage, protobuf)

        self.schema_computation = SchemaComputation(self)
        self.to_parquet_computation = ToParquetComputation(
            self, arrow_remote=ToArrowComputationOnServer(self)
        )
        self.to_arrow_computation = ToArrowComputation(
            self,
            parquet_computation=self.to_parquet_computation,
            arrow_remote=self.to_parquet_computation.remote_arrow,
        )
        self.cache_scalar_computation = CacheScalarComputation(
            self, ValueComputationOnServer(self)
        )
        self.value_computation = ValueComputation(
            self,
            cache_scalar_computation=self.cache_scalar_computation,
            remote_scalar=self.cache_scalar_computation.remote_scalar,
        )

        self._client = client
        self._mock_size = 1000
        self._parquet_dir = os.path.join(tempfile.mkdtemp(), "sarus_dataspec")
        os.makedirs(self._parquet_dir, exist_ok=True)

    def set_admin_ds(
        self, source_ds: st.DataSpec, admin_ds: t.Dict[str, t.Any]
    ) -> None:
        """Attach the admin_ds to a source dataspec in a status."""
        assert source_ds.is_source()
        if source_ds.status([ADMIN_DS]) is None:
            stt.ready(
                source_ds,
                task=ADMIN_DS,
                properties={ADMIN_DS: json.dumps(admin_ds)},
            )

    def default_delta(self, dataspec: st.DataSpec) -> t.Optional[float]:
        """Get the default delta of a dataspec."""
        sources_ds = dataspec.sources(sp.type_name(sp.Dataset))
        sources_ds = [
            source for source in sources_ds if not source.is_public()
        ]
        source = sources_ds.pop()
        status = source.status(task_names=[ADMIN_DS])
        if status is None:
            return None
        stage = status.task(task=ADMIN_DS)
        assert stage.ready()
        admin_ds = json.loads(stage[ADMIN_DS])
        # TODO : revise this when the API provides a unified endpoint for
        # applied access rule
        delta = admin_ds.get("accesses").pop(0).get("delta")
        return float(delta)

    def consumed_epsilon(self, dataspec: st.DataSpec) -> float:
        """Get the consumed epsilon from the server."""
        # TODO works only when the value is already computed on the server side
        epsilon = api.get_epsilon(self.client(), dataspec.uuid())
        return epsilon

    def client(self) -> Client:
        """Return the sarus.Client object used to make API calls."""
        return self._client

    def is_cached(self, dataspec: st.DataSpec) -> bool:
        """Return True if the dataspec is cached locally."""
        return True

    def is_computation_remote(self, dataspec: st.DataSpec) -> bool:
        """Return True if the dataspec is remotely computed."""
        # `select_sql` transforms are delegated, whether mock or not
        if dataspec.is_transformed():
            transform = dataspec.transform()
            if transform.protobuf().spec.HasField(
                "select_sql"
            ) or transform.protobuf().spec.HasField("dp_select_sql"):
                computation_graph = self.computation_graph(dataspec)
                referrables = list(computation_graph["dataspecs"]) + list(
                    computation_graph["transforms"]
                )
                api.push_dataspec_graph(self._client, referrables)

        ds = api.get_dataspec(self.client(), dataspec.uuid())
        return ds is not None

    def is_big_data(self, dataset: st.Dataset) -> bool:
        """Method to compute is_big data.

        Method to compute is_big data if the status
        is not in the storage and the dataset is source
        we retrieve it via an api call
        """
        last_status = self.status(dataset, task_name=BIG_DATA_TASK)
        if last_status:
            stage = last_status.task(task=BIG_DATA_TASK)
            is_big = stage.properties().get(IS_BIG_DATA)
            return is_big == str(True)

        if dataset.is_source():
            status_proto = api.dataspec_status(
                self.client(), dataset.uuid(), task_names=[BIG_DATA_TASK]
            )
            stt.ready(
                dataset,
                manager=self,
                task=BIG_DATA_TASK,
                properties=status_proto.task_stages[BIG_DATA_TASK].properties,
            )
            return status_proto.task_stages[BIG_DATA_TASK].properties[
                IS_BIG_DATA
            ] == str(True)
        return super().is_big_data(dataset)

    def push(self, dataspec: st.DataSpec) -> None:
        """Push a Dataspec's computation graph on the server."""
        computation_graph = self.computation_graph(dataspec)
        referrables = list(computation_graph["dataspecs"]) + list(
            computation_graph["transforms"]
        )
        api.push_dataspec_graph(self.client(), referrables)

    def rewrite(
        self, dataspec: st.DataSpec, target_epsilon: t.Optional[float] = None
    ) -> t.Tuple[st.DataSpec, DataspecPrivacyPolicy]:
        """Rewrite an alternative Dataspec."""
        if target_epsilon is not None:
            default_delta = self.default_delta(dataspec)
            if default_delta is None:
                raise ValueError(f"Default delta not defined for {dataspec}")
            privacy_limit = DeltaEpsilonLimit({default_delta: target_epsilon})
        else:
            privacy_limit = None

        alt_dataspec_uuid, privacy_policy = api.rewrite_dataspec(
            self.client(), dataspec.uuid(), privacy_limit=privacy_limit
        )
        api.pull_dataspec_graph(self.client(), alt_dataspec_uuid)
        alt_dataspec = self.storage().referrable(alt_dataspec_uuid)
        return alt_dataspec, privacy_policy

    def launch(self, dataspec: st.DataSpec) -> None:
        """Launch a Dataspec's computation on the server."""
        api.launch_dataspec(self.client(), dataspec.uuid())

    def python_type(self, dataspec: st.DataSpec) -> str:
        """Return the Python class name of a DataSpec.

        This is used to instantiate the correct DataSpecWrapper class.
        """
        python_type_att = dataspec.attribute(name=PYTHON_TYPE)
        if python_type_att is not None:
            return python_type_att.properties().get(PYTHON_TYPE)

        if not dataspec.is_transformed():
            return str(t.Iterator[pa.RecordBatch])

        transform = dataspec.transform()
        if not transform.is_external():
            # TODO: have a python type in SDS for all transforms
            if transform.spec() in ['fit_model', 'fit_model_dp']:
                type_str = str(TrainState)
            else:
                type_str = str(t.Iterator[pa.RecordBatch])
        else:
            ds_args, ds_kwargs = dataspec.parents()
            mock_value = self.mock_value(transform, *ds_args, **ds_kwargs)
            type_str = str(type(mock_value))

        attach_properties(
            dataspec, name=PYTHON_TYPE, properties={PYTHON_TYPE: type_str}
        )
        return type_str

    Edge = t.Tuple[st.DataSpec, st.DataSpec, st.Transform]

    def computation_graph(
        self,
        dataspec: st.DataSpec,
    ) -> t.Dict[str, t.Union[st.DataSpec, st.Transform, st.Attribute, Edge]]:
        """Retreive all items necessary to compute a DataSpec.

        This function is used intensively to post DataSpecs, draw dot
        representationss, fetch statuses, and so on.
        """
        storage = self.storage()

        class ComputationGraphVisitor(st.Visitor, st.TransformVisitor):
            dataspecs: t.List[st.DataSpec] = list()
            transforms: t.Set[st.Transform] = set()
            lambdas: t.Set[st.Transform] = set()
            edges: t.Set[
                t.Tuple[st.DataSpec, st.DataSpec, st.Transform]
            ] = set()
            attributes: t.Set[st.Attribute] = set()
            variant_constraints: t.Set[st.VariantConstraint] = set()
            graph: t.Dict[str, t.Set[str]] = dict()

            def transformed(
                self,
                visited: st.DataSpec,
                transform: st.Transform,
                *arguments: st.DataSpec,
                **named_arguments: st.DataSpec,
            ) -> None:
                if visited not in self.dataspecs:
                    self.dataspecs.append(visited)

                    attributes: t.List[st.Attribute] = storage.referring(
                        visited, type_name=sp.type_name(sp.Attribute)
                    )
                    # Don't send MOCK and PYTHON_TYPE attributes to the server
                    self.attributes.update(
                        [
                            att
                            for att in attributes
                            if att.name() not in [MOCK, PYTHON_TYPE]
                        ]
                    )

                    variant_constraints = storage.referring(
                        visited, type_name=sp.type_name(sp.VariantConstraint)
                    )
                    self.variant_constraints.update(
                        [vc for vc in variant_constraints]
                    )

                    self.transforms.add(transform)
                    for argument in arguments:
                        argument.accept(self)
                        self.edges.add((argument, visited, transform))
                        if isinstance(argument, st.Transform):
                            self.lambdas.add(argument)
                    for _, argument in named_arguments.items():
                        argument.accept(self)
                        self.edges.add((argument, visited, transform))
                        if isinstance(argument, st.Transform):
                            self.lambdas.add(argument)

            def other(self, visited: st.DataSpec) -> None:
                if visited not in self.dataspecs:
                    assert isinstance(visited, st.DataSpec)
                    self.dataspecs.append(visited)

            def composed(
                self,
                visited: st.Transform,
                transform: st.Transform,
                *arguments: st.Transform,
                **named_arguments: st.Transform,
            ) -> None:
                self.transforms.add(visited)
                self.transforms.add(transform)
                for argument in arguments:
                    argument.accept(self)
                for _, argument in named_arguments.items():
                    argument.accept(self)

            def variable(
                self,
                visited: st.Transform,
                name: str,
                position: int,
            ) -> None:
                self.transforms.add(visited)

        visitor = ComputationGraphVisitor()
        dataspec.accept(visitor)

        return {
            "dataspecs": visitor.dataspecs,
            "transforms": visitor.transforms,
            "attributes": visitor.attributes,
            "variant_constraints": visitor.variant_constraints,
            "edges": visitor.edges,
            "lambdas": visitor.lambdas,
        }

    def has_transform(
        self,
        dataspec: st.DataSpec,
        transform_name: str,
    ) -> bool:
        """Check if the computation graph contains some transforms.

        This function is used to check if we have rewritten the computation graph to
        turn big data dataspec into smaller one.
        """

        class HasTransformVisitor(st.Visitor, st.TransformVisitor):
            dataspecs: t.List[st.DataSpec] = list()
            transforms: t.Set[st.Transform] = set()
            has_transform: bool = False
            transform_of_interest: t.Optional[st.Transform] = None

            def transformed(
                self,
                visited: st.DataSpec,
                transform: st.Transform,
                *arguments: st.DataSpec,
                **named_arguments: st.DataSpec,
            ) -> None:
                if visited not in self.dataspecs:
                    self.dataspecs.append(visited)
                    if transform.name() == transform_name:
                        self.has_transform = True
                        self.transform_of_interest = transform
                    else:
                        self.transforms.add(transform)
                        for argument in arguments:
                            argument.accept(self)
                        for _, argument in named_arguments.items():
                            argument.accept(self)

            def other(self, visited: st.DataSpec) -> None:
                if visited not in self.dataspecs:
                    assert isinstance(visited, st.DataSpec)
                    self.dataspecs.append(visited)

            def composed(
                self,
                visited: st.Transform,
                transform: st.Transform,
                *arguments: st.Transform,
                **named_arguments: st.Transform,
            ) -> None:
                self.transforms.add(visited)
                self.transforms.add(transform)
                for argument in arguments:
                    argument.accept(self)
                for _, argument in named_arguments.items():
                    argument.accept(self)

            def variable(
                self,
                visited: st.Transform,
                name: str,
                position: int,
            ) -> None:
                self.transforms.add(visited)

        visitor = HasTransformVisitor()
        dataspec.accept(visitor)
        return visitor.has_transform, visitor.transform_of_interest

    def _delete_local(self, uuid: str) -> None:
        """Delete a DataSpec locally. MOCKs also have to be deleted."""
        would_delete = self.storage().all_referrings(uuid)
        additional_cleanup = []
        for uuid in would_delete:
            item = self.storage().referrable(uuid)
            if item.prototype() in [sp.Dataset, sp.Scalar]:
                try:
                    mock = item.variant(st.ConstraintKind.MOCK)
                except Exception:
                    pass
                else:
                    if mock:
                        additional_cleanup.append(mock)

        self.storage().delete(uuid)
        for item in additional_cleanup:
            self.storage().delete(item.uuid())

    def dot(
        self,
        dataspec: st.DataSpec,
        symbols: t.Dict[str, t.Optional[str]] = dict(),
        policy: t.Optional[DataspecPrivacyPolicy] = None,
        remote: bool = True,
        task_names: t.List[str] = [ARROW_TASK, SCALAR_TASK],
    ) -> str:
        """Graphviz dot language representation of the graph.

        Statuses are represented with a color code. The symbols are the
        caller's symbol for the DataSpec wrapper
        (see DataSpecWrapper.dataspec_wrapper_symbols).
        """
        api.pull_dataspec_graph(self.client(), dataspec.uuid())
        graph = self.computation_graph(dataspec)

        # Filter all the dataspecs that are above the source dataset
        source_ds = [
            ds
            for ds in graph["dataspecs"]
            if ds.is_transformed() and ds.transform().spec() == "assign_budget"
        ]
        syn_ds = [
            ds
            for ds in graph["dataspecs"]
            if ds.is_transformed() and ds.transform().spec() == "synthetic"
        ]
        top_ds = syn_ds[0] if syn_ds else source_ds[0]
        onboarded_graph = self.computation_graph(top_ds)

        dataspecs_to_show = (
            set(graph["dataspecs"]) - set(onboarded_graph["dataspecs"])
        ) | {top_ds}
        edges_to_show = set(graph["edges"]) - set(onboarded_graph["edges"])

        TASK = (
            ARROW_TASK if dataspec.prototype() == sp.Dataset else SCALAR_TASK
        )

        # Get statuses wether remote or local
        if remote:
            statuses_proto = api.pull_dataspec_status_graph(
                self._client, dataspec.uuid(), task_names
            )
            statuses = {
                proto.dataspec: stt.Status(proto, store=False)
                for proto in statuses_proto
            }
        else:
            statuses = {
                ds.uuid(): stt.last_status(ds, task=TASK)
                for ds in dataspecs_to_show
            }

        # Transform names to SDK's identifiers
        from sarus.scripts.generate_op_list import op_list

        op_mapping = op_list()

        def transform_label(name: str) -> str:
            """Map the transform name to the SDK's name."""
            if name.endswith("_DP"):
                is_dp = True
                name = name[:-3]
            else:
                is_dp = False

            info = op_mapping[op_mapping.code == name]
            if info.shape[0] == 0:
                if name == "dp_select_sql":
                    return "dp_sql"
                return name
            info = info.iloc[0]
            if pd.isna(info.function):
                label = info.method
            else:
                label = info.function

            if is_dp:
                label = f"dp_{label}"

            return label

        # Add nodes
        edges, nodes, props, lambdas = [], [], [], []
        for ds in dataspecs_to_show:
            status = statuses.get(ds.uuid())
            if ds.uuid() == dataspec.uuid():
                nodes.append(
                    self.dataspec_repr(ds, status, symbols, policy=policy)
                )
            else:
                nodes.append(self.dataspec_repr(ds, status, symbols))

        edges_dict = defaultdict(list)
        for parent, child, transform in edges_to_show:
            tr_label = transform_label(transform.name())
            edges_dict[(child.uuid(), tr_label)].append(parent.uuid())

        for (child, tr_label), parents in edges_dict.items():
            if len(parents) == 1:
                parent = parents.pop()
                edges.append(
                    f'"{parent}" -> "{child}" ' f'[label="{tr_label}"];'
                )
            else:
                # concentrate the edges
                # https://mike42.me/blog/2015-02-how-to-merge-edges-in-graphviz
                intermediate = f"{child}_intermediate"
                parents = map(lambda x: f'"{x}"', parents)
                edges.append(
                    f'"{intermediate}" [shape=point,width=0.01,height=0.01];\n'
                    f'{{{", ".join(parents)}}} -> "{intermediate}" [dir=none];\n'
                    f'"{intermediate}" -> "{child}" [label="{tr_label}"];'
                )

        for i, transform in enumerate(graph["lambdas"]):
            lambdas.append(
                transform.dot().replace(
                    "digraph {",
                    f'subgraph cluster_{i} {{\ncolor=black;\nlabel="Traced function";',
                )
            )

        props = [
            "nodesep=0.1;",
            "ranksep=0.1;",
            'node [style="rounded,filled" fontsize="12" margin="0.055,0.055"]',
            'edge [fontsize="10" fontname="Liberation Mono:style=Regular"]',
        ]
        dot = ["digraph {"] + props + nodes + edges + lambdas + ["}"]
        return "\n".join(dot)

    def dataspec_repr(
        self,
        dataspec: st.DataSpec,
        status: t.Optional[st.Status],
        symbols: t.Dict[str, t.Optional[str]],
        info: t.Literal["status", "privacy"] = "privacy",
        policy: t.Optional[DataspecPrivacyPolicy] = None,
    ) -> str:
        """Style a graph node depending on its status and symbol."""
        # Colors tuple represent (fillcolor, color, fontcolor)
        STATUS_COLORS = {
            "error": ("#ff9c9c", "black", "black"),
            "ready": ("#9cffc5", "black", "black"),
            "pending": ("#ffc89c", "black", "black"),
            "processing": ("#9cbeff", "black", "black"),
            "no_status": ("#ffffff", "#ff9c9c", "black"),
        }
        PRIVACY_COLORS = {
            "PEP": ("#428e92", "#428e92", "white"),
            "DP": ("#006064", "#006064", "white"),
            "NOT_PEP": ("white", "#428e92", "#428e92"),
        }
        if info == "status":
            TASK = (
                ARROW_TASK
                if dataspec.prototype() == sp.Dataset
                else SCALAR_TASK
            )
            stage = status.task(TASK) if status else None
            key = stage.stage() if stage else "no_status"
            fillcolor, color, fontcolor = STATUS_COLORS[key]
        else:
            if dataspec.is_dp():
                key = "DP"
            elif dataspec.is_pep():
                key = "PEP"
            else:
                key = "NOT_PEP"

            fillcolor, color, fontcolor = PRIVACY_COLORS[key]

        # Dataspec name
        name = ""
        ds_name = dataspec.name()
        if dataspec.is_transformed():
            transform = dataspec.transform()
            if transform.spec() == "synthetic":
                name = "synthetic_data\n"
            elif transform.spec() == "assign_budget":
                name = "source_data\n"
            elif transform.spec() == "derive_seed":
                name = "local_seed"
            else:
                name = f"{ds_name}\n" if ds_name != "Transformed" else ""
        else:
            if ds_name == "seed":
                name = "master_seed"
            else:
                name = ds_name

        # Class & variable name
        var_name, classname = symbols.get(dataspec.uuid(), ("", ""))
        name = var_name if var_name else name
        classname = f" ({classname})" if classname else classname

        # Status info
        status_msg = ""
        if info == "status":
            if stage:
                status_msg = (
                    stage.properties().get("message", "").replace('"', "'")
                )
            else:
                status_msg = "No status found."
            if status_msg:
                status_msg = "\n" + status_msg

        # Privacy type
        pep_type = " (PEP)" if dataspec.is_pep() else ""

        # Privacy policy
        policy_msg = ""
        if policy:
            policy_msg = {
                DataspecPrivacyPolicy.WHITE_LISTED: "Whitelisted",
                DataspecPrivacyPolicy.DP: "Differentially-Private",
                DataspecPrivacyPolicy.SYNTHETIC: "Synthetic",
                DataspecPrivacyPolicy.PUBLIC: "Public",
            }[policy]
            policy_msg = f"{policy_msg}\n"

        # Assemble
        label = f"{policy_msg}{name}{classname}{pep_type}"
        return (
            f'"{dataspec.uuid()}"[label="{label}", '
            f'fillcolor="{fillcolor}", color="{color}", '
            f'fontcolor="{fontcolor}" shape="box"]'
        )

    async def async_schema_op(self, dataset: st.Dataset) -> st.Schema:
        # quickfix for select sql, to be removed when there is an endpoint
        # for schema
        if dataset.is_transformed() and (
            dataset.transform().spec() == "select_sql"
            or dataset.transform().spec() == "dp_select_sql"
        ):
            return api.pull_dataspec_schema(self._client, dataset.uuid())

        if dataset.is_transformed():
            return await TransformedDataset(dataset).schema()
        else:
            raise ValueError("Dataset should be transformed.")

    async def async_to_arrow_op(
        self, dataset: st.Dataset, batch_size: int
    ) -> t.AsyncIterator[pa.RecordBatch]:
        """Route a Dataset to its Op implementation.

        When the computation is not delegated the manager should also be
        able to compute the value.
        """
        if dataset.is_transformed():
            iterator = await TransformedDataset(dataset).to_arrow(
                batch_size=batch_size
            )
            return iterator

        else:
            raise ValueError("Dataset should be transformed.")

    async def async_value_op(self, scalar: st.Scalar) -> t.Any:
        """Route a Scalar to its Op implementation.

        This method is shared between API and Worker because when the data is
        not cached the API manager should also be able to compute the value.
        """
        if scalar.is_transformed():
            return await TransformedScalar(scalar).value()
        else:
            return await SourceScalar(scalar).value()

    def copy_status_from_server(
        self, dataspec: st.DataSpec, task_names: t.List[str]
    ) -> None:
        """Method to temporary to retrieve the schemas.

        This method is to be used only temporary to retrieve the
        schemas from the server when a dataset is created.
        """
        status = api.dataspec_status(
            self.client(), dataspec.uuid(), task_names=task_names
        )
        for task_name in task_names:
            if dataspec.status([task_name]) is None:
                stt.ready(
                    dataspec,
                    manager=self,
                    task=task_name,
                    properties=status.task_stages[task_name].properties,
                )

    def dataspec_computation(
        self,
        dataspec: st.DataSpec,
    ) -> BaseComputation:
        """Return the computation for a DataSpec."""
        proto = dataspec.prototype()
        if proto == sp.Dataset:
            return self.to_arrow_computation
        return self.value_computation

    def computation_timeout(self, dataspec: st.DataSpec) -> int:
        return 1800

    def computation_max_delay(self, dataspec: st.DataSpec) -> int:
        return 10


def manager(
    storage: storage_typing.Storage, client, **kwargs: t.Any
) -> SDKManager:
    """Create the SDK manager."""
    properties = {"type": "sdk_manager"}
    properties.update(kwargs)
    return SDKManager(
        storage=storage,
        protobuf=sp.Manager(properties=properties),
        client=client,
    )
