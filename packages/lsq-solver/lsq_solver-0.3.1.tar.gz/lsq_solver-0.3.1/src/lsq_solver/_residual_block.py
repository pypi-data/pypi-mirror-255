from dataclasses import dataclass

from lsq_solver.auto_diff import make_jac


@dataclass
class _ResidualBlock:
    """
    DO NOT USE THIS CLASS DIRECTLY!
    """

    dim_residual: int
    residual_func: callable
    dim_variable: int = 0
    loss_func = None
    jac_func = None
    jac_sparsity = None

    def __post_init__(self):
        self.row_range = (0, 0)
        self.col_ranges = []

    def make_jacobian(self, jac_func, dim_residual: int, dim_variable: int, residual_func):
        self.jac_func = make_jac(jac_func, (dim_residual, dim_variable), residual_func)
