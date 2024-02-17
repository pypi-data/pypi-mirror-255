from sarus.utils import register_ops

try:
    from plotly.express import *  # noqa: F401
except ModuleNotFoundError:
    pass
else:
    register_ops()
