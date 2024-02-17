from sarus.dataspec_wrapper import DataSpecWrapper
from sarus.utils import register_ops, sarus_init

try:
    import ydata_profiling
except ModuleNotFoundError:
    pass


class ProfileReport(DataSpecWrapper[ydata_profiling.ProfileReport]):
    @sarus_init("pandas_profiling.PD_PROFILE_REPORT")
    def __init__(self, df=None, **kwargs) -> None:
        ...


register_ops()
