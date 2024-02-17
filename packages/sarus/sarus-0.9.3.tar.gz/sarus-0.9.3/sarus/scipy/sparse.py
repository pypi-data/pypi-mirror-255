from __future__ import annotations

import logging
from functools import partial

from sarus.dataspec_wrapper import DataSpecWrapper
from sarus.utils import register_ops, sarus_init, sarus_method, sarus_property

try:
    from scipy.sparse import (
        bsr_array,
        bsr_matrix,
        coo_array,
        coo_matrix,
        csc_array,
        csc_matrix,
        csr_array,
        csr_matrix,
        dia_array,
        dia_matrix,
        dok_array,
        dok_matrix,
        lil_array,
        lil_matrix,
    )
except ModuleNotFoundError:
    pass

logger = logging.getLogger(__name__)

sarus_method = partial(sarus_method)
sarus_property = partial(sarus_property)
sarus_init = partial(sarus_init)


class bsr_matrix(DataSpecWrapper[bsr_matrix]):
    @sarus_init("scipy.SCIPY_BSR_MATRIX")
    def __init__(
        self,
        arg1,
        shape=None,
        dtype=None,
        copy=False,
        blocksize=None,
    ):
        ...

    @sarus_method("scipy.SCIPY_ELIMINATE_ZEROS", inplace=True)
    def eliminate_zeros(self):
        ...

    @sarus_method("scipy.SCIPY_SORT_INDICES", inplace=True)
    def sorted_indices(self):
        ...

    @sarus_method("scipy.SCIPY_SUM_DUPLICATES", inplace=True)
    def sum_duplicates(self):
        ...


class coo_matrix(DataSpecWrapper[coo_matrix]):
    @sarus_init("scipy.SCIPY_COO_MATRIX")
    def __init__(
        self,
        arg1,
        shape=None,
        dtype=None,
        copy=False,
    ):
        ...

    @sarus_method("scipy.SCIPY_ELIMINATE_ZEROS", inplace=True)
    def eliminate_zeros(self):
        ...

    @sarus_method("scipy.SCIPY_SORT_INDICES", inplace=True)
    def sorted_indices(self):
        ...

    @sarus_method("scipy.SCIPY_SUM_DUPLICATES", inplace=True)
    def sum_duplicates(self):
        ...


class csc_matrix(DataSpecWrapper[csc_matrix]):
    @sarus_init("scipy.SCIPY_CSC_MATRIX")
    def __init__(
        self,
        arg1=None,
        shape=None,
        dtype=None,
        copy=False,
    ):
        ...

    @sarus_method("scipy.SCIPY_ELIMINATE_ZEROS", inplace=True)
    def eliminate_zeros(self):
        ...

    @sarus_method("scipy.SCIPY_SORT_INDICES", inplace=True)
    def sorted_indices(self):
        ...

    @sarus_method("scipy.SCIPY_SUM_DUPLICATES", inplace=True)
    def sum_duplicates(self):
        ...


class csr_matrix(DataSpecWrapper[csr_matrix]):
    @sarus_init("scipy.SCIPY_CSR_MATRIX")
    def __init__(
        self,
        arg1=None,
        shape=None,
        dtype=None,
        copy=False,
    ):
        ...

    @sarus_method("scipy.SCIPY_ELIMINATE_ZEROS", inplace=True)
    def eliminate_zeros(self):
        ...

    @sarus_method("scipy.SCIPY_SORT_INDICES", inplace=True)
    def sorted_indices(self):
        ...

    @sarus_method("scipy.SCIPY_SUM_DUPLICATES", inplace=True)
    def sum_duplicates(self):
        ...


class dia_matrix(DataSpecWrapper[dia_matrix]):
    @sarus_init("scipy.SCIPY_DIA_MATRIX")
    def __init__(
        self,
        arg1,
        shape=None,
        dtype=None,
        copy=False,
    ):
        ...

    @sarus_method("scipy.SCIPY_ELIMINATE_ZEROS", inplace=True)
    def eliminate_zeros(self):
        ...

    @sarus_method("scipy.SCIPY_SORT_INDICES", inplace=True)
    def sorted_indices(self):
        ...

    @sarus_method("scipy.SCIPY_SUM_DUPLICATES", inplace=True)
    def sum_duplicates(self):
        ...


class dok_matrix(DataSpecWrapper[dok_matrix]):
    @sarus_init("scipy.SCIPY_DOK_MATRIX")
    def __init__(
        self,
        arg1=None,
        shape=None,
        dtype=None,
        copy=False,
    ):
        ...

    @sarus_method("scipy.SCIPY_ELIMINATE_ZEROS", inplace=True)
    def eliminate_zeros(self):
        ...

    @sarus_method("scipy.SCIPY_SORT_INDICES", inplace=True)
    def sorted_indices(self):
        ...

    @sarus_method("scipy.SCIPY_SUM_DUPLICATES", inplace=True)
    def sum_duplicates(self):
        ...


class lil_matrix(DataSpecWrapper[lil_matrix]):
    @sarus_init("scipy.SCIPY_LIL_MATRIX")
    def __init__(
        self,
        arg1=None,
        shape=None,
        dtype=None,
        copy=False,
    ):
        ...

    @sarus_method("scipy.SCIPY_ELIMINATE_ZEROS", inplace=True)
    def eliminate_zeros(self):
        ...

    @sarus_method("scipy.SCIPY_SORT_INDICES", inplace=True)
    def sorted_indices(self):
        ...

    @sarus_method("scipy.SCIPY_SUM_DUPLICATES", inplace=True)
    def sum_duplicates(self):
        ...


class bsr_array(DataSpecWrapper[bsr_array]):
    @sarus_init("scipy.SCIPY_BSR_ARRAY")
    def __init__(
        self,
        arg1,
        shape=None,
        dtype=None,
        copy=False,
        blocksize=None,
    ):
        ...

    @sarus_method("scipy.SCIPY_ELIMINATE_ZEROS", inplace=True)
    def eliminate_zeros(self):
        ...

    @sarus_method("scipy.SCIPY_SORT_INDICES", inplace=True)
    def sorted_indices(self):
        ...

    @sarus_method("scipy.SCIPY_SUM_DUPLICATES", inplace=True)
    def sum_duplicates(self):
        ...


class coo_array(DataSpecWrapper[coo_array]):
    @sarus_init("scipy.SCIPY_COO_ARRAY")
    def __init__(self, arg1, shape=None, dtype=None, copy=False):
        ...

    @sarus_method("scipy.SCIPY_ELIMINATE_ZEROS", inplace=True)
    def eliminate_zeros(self):
        ...

    @sarus_method("scipy.SCIPY_SORT_INDICES", inplace=True)
    def sorted_indices(self):
        ...

    @sarus_method("scipy.SCIPY_SUM_DUPLICATES", inplace=True)
    def sum_duplicates(self):
        ...


class csc_array(DataSpecWrapper[csc_array]):
    @sarus_init("scipy.SCIPY_CSC_ARRAY")
    def __init__(self, arg1, shape=None, dtype=None, copy=False):
        ...

    @sarus_method("scipy.SCIPY_ELIMINATE_ZEROS", inplace=True)
    def eliminate_zeros(self):
        ...

    @sarus_method("scipy.SCIPY_SORT_INDICES", inplace=True)
    def sorted_indices(self):
        ...

    @sarus_method("scipy.SCIPY_SUM_DUPLICATES", inplace=True)
    def sum_duplicates(self):
        ...


class csr_array(DataSpecWrapper[csr_array]):
    @sarus_init("scipy.SCIPY_CSR_ARRAY")
    def __init__(self, arg1, shape=None, dtype=None, copy=False):
        ...

    @sarus_method("scipy.SCIPY_ELIMINATE_ZEROS", inplace=True)
    def eliminate_zeros(self):
        ...

    @sarus_method("scipy.SCIPY_SORT_INDICES", inplace=True)
    def sorted_indices(self):
        ...

    @sarus_method("scipy.SCIPY_SUM_DUPLICATES", inplace=True)
    def sum_duplicates(self):
        ...


class dia_array(DataSpecWrapper[dia_array]):
    @sarus_init("scipy.SCIPY_DIA_ARRAY")
    def __init__(self, arg1, shape=None, dtype=None, copy=False):
        ...

    @sarus_method("scipy.SCIPY_ELIMINATE_ZEROS", inplace=True)
    def eliminate_zeros(self):
        ...

    @sarus_method("scipy.SCIPY_SORT_INDICES", inplace=True)
    def sorted_indices(self):
        ...

    @sarus_method("scipy.SCIPY_SUM_DUPLICATES", inplace=True)
    def sum_duplicates(self):
        ...


class dok_array(DataSpecWrapper[dok_array]):
    @sarus_init("scipy.SCIPY_DOK_ARRAY")
    def __init__(self, arg1, shape=None, dtype=None, copy=False):
        ...

    @sarus_method("scipy.SCIPY_ELIMINATE_ZEROS", inplace=True)
    def eliminate_zeros(self):
        ...

    @sarus_method("scipy.SCIPY_SORT_INDICES", inplace=True)
    def sorted_indices(self):
        ...

    @sarus_method("scipy.SCIPY_SUM_DUPLICATES", inplace=True)
    def sum_duplicates(self):
        ...


class lil_array(DataSpecWrapper[lil_array]):
    @sarus_init("scipy.SCIPY_LIL_ARRAY")
    def __init__(self, arg1, shape=None, dtype=None, copy=False):
        ...

    @sarus_method("scipy.SCIPY_ELIMINATE_ZEROS", inplace=True)
    def eliminate_zeros(self):
        ...

    @sarus_method("scipy.SCIPY_SORT_INDICES", inplace=True)
    def sorted_indices(self):
        ...

    @sarus_method("scipy.SCIPY_SUM_DUPLICATES", inplace=True)
    def sum_duplicates(self):
        ...


register_ops()
