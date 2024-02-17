"""SDK classes and functions."""
# flake8: noqa
import warnings

VERSION = "0.9.3"

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    from sarus import (
        imblearn,
        numpy,
        pandas,
        pandas_profiling,
        plotly,
        scipy,
        shap,
        sklearn,
        skopt,
        std,
        xgboost,
        optbinning,
    )

    from .sarus import Client, Dataset
    from .utils import (
        eval,
        eval_perturbation,
        eval_policy,
        floating,
        integer,
        length,
    )


__all__ = [
    "Dataset",
    "Client",
    "length",
    "eval",
    "eval_perturbation",
    "eval_policy",
    "config",
    "floating",
    "integer",
]
