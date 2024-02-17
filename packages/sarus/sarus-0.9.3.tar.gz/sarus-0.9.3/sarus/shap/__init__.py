"""Sarus Shap package documentation."""
# flake8: noqa
from sarus.utils import register_ops

try:
    from shap import *

    from .explainers import Additive as AdditiveExplainer
    from .explainers import *
    from .explainers import Explainer
    from .explainers import GPUTree as GPUTreeExplainer
    from .explainers import Kernel as KernelExplainer
    from .explainers import Linear as LinearExplainer
    from .explainers import Partition as PartitionExplainer
    from .explainers import Permutation as PermutationExplainer
    from .explainers import Sampling as SamplingExplainer
    from .explainers import Tree as TreeExplainer
    from .Explanation import *
    from .maskers import *
    from .plots import *
    from .utils import *
except ModuleNotFoundError:
    bar_plot = None
    summary_plot = None
    decision_plot = None
    multioutput_decision_plot = None
    embedding_plot = None
    force_plot = None
    save_html = None
    group_difference_plot = None
    image_plot = None
    monitoring_plot = None
    partial_dependence_plot = None
    dependence_plot = None
    text_plot = None
    waterfall_plot = None
    initjs = None


register_ops()
