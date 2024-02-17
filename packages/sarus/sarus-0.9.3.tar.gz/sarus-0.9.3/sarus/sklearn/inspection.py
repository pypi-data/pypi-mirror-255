from sarus.utils import register_ops

try:
    from sklearn.inspection import *  # noqa: F401
except ModuleNotFoundError:
    pass  # error message in sarus_data_spec.typing


register_ops()
