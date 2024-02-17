import numpy as np
from scipy.optimize import least_squares
from scipy.sparse import dok_matrix

from lsq_solver._residual_block import _ResidualBlock
from lsq_solver.loss_funcs import make_loss


class LeastSquaresProblem:
    def __init__(self):
        self._dim_variable = 0
        self._dim_residual = 0
        self._address_col_range_map = {}
        self._col_range_variable_map = {}
        self._residual_blocks = []
        self._x0 = None
        self._jac_sparsity = None
        self._fixed_variable_address = set()
        self._address_bounds_map = {}
        self._bounds = None

    def add_residual_block(
        self,
        dim_residual: int,
        residual_func: callable,
        *variables,
        loss_func="linear",
        f_scale=1.0,
        jac_func="2-point",
        jac_sparsity=None,
    ):
        if dim_residual <= 0:
            err_msg = f"dim_residual should > 0, got {dim_residual}"
            raise ValueError(err_msg)
        if not callable(residual_func):
            err_msg = "residual_func should be callable"
            raise TypeError(err_msg)
        residual_block = _ResidualBlock(dim_residual=dim_residual, residual_func=residual_func)

        if callable(loss_func):
            residual_block.loss_func = loss_func
        else:
            residual_block.loss_func = make_loss(loss_func, f_scale=f_scale)

        residual_block.row_range = (self._dim_residual, self._dim_residual + dim_residual)
        self._dim_residual += dim_residual

        residual_block.col_ranges = []
        for variable in variables:
            if len(variable.shape) != 1:
                err_msg = f"Variable should only have one axis, got {len(variable.shape)}"
                raise ValueError(err_msg)
            variable_dim = variable.shape[0]
            residual_block.dim_variable += variable_dim

            address = variable.__array_interface__["data"][0]
            if address not in self._address_col_range_map:
                new_range = (self._dim_variable, self._dim_variable + variable_dim)
                self._dim_variable += variable_dim
                self._address_col_range_map[address] = new_range
                self._col_range_variable_map[new_range] = variable
            residual_block.col_ranges.append(self._address_col_range_map[address])

        if callable(jac_func):
            residual_block.jac_func = jac_func
        else:
            residual_block.make_jacobian(
                jac_func, residual_block.dim_residual, residual_block.dim_variable, residual_block.residual_func
            )

        if jac_sparsity is None:
            residual_block.jac_sparsity = None
        else:
            if jac_sparsity.shape[0] != dim_residual or jac_sparsity.shape[1] != residual_block.dim_variable:
                err_msg = f"jac shape {jac_sparsity.shape} not equal to ({dim_residual}, {residual_block.dim_variable})"
            residual_block.jac_sparsity = jac_sparsity.copy()

        self._residual_blocks.append(residual_block)

    def fix_variables(self, *variables):
        for variable in variables:
            self._fixed_variable_address.add(variable.__array_interface__["data"][0])

    def unfix_variables(self, *variables):
        for variable in variables:
            address = variable.__array_interface__["data"][0]
            if address in self._fixed_variable_address:
                self._fixed_variable_address.remove(address)

    def bound_variable(self, variable: np.ndarray, lower_bound=-np.inf, upper_bound=np.inf):
        """
        Lower and upper bounds on independent variable. Defaults to no bounds.
        Note that the initial value of a bounded variable must lie in the boundary.
        :param variable:
        :param min: array_like or scalar
            The array must match the size of variable or be a scalar. -np.inf means no bound.
        :param max: array_like or scalar
            The array must match the size of variable or be a scalar. np.inf means no bound.
        :return: None
        """
        address = variable.__array_interface__["data"][0]
        col_range = self._address_col_range_map[address]
        if not (np.isscalar(lower_bound) or lower_bound.shape[0] == col_range[1] - col_range[0]):
            err_msg = "Lower bound error"
            raise ValueError(err_msg)
        if not (np.isscalar(upper_bound) or upper_bound.shape[0] == col_range[1] - col_range[0]):
            err_msg = "Upper bound error"
            raise ValueError(err_msg)
        self._address_bounds_map[address] = (lower_bound, upper_bound)

    def solve(self, method="trf", ftol=1e-8, xtol=1e-8, gtol=1e-8, max_nfev=None, x_scale="jac", verbose=0):
        """
        solve the problem.
        :param method: {'trf', 'dogleg', 'lm'}
            - trf: Trust Region Reflective algorithm, particular suitable for large sparse problem with bounds.
            - dogleg: dogleg algorithm with rectangle trust region, typical use case is small problems with bounds.
            - lm: Levenberg-Marquardt algorithm. Doesn't handle bounds and sparse jacobians. Suit for small problem.
        :param ftol: float
            Tolerance for termination by the change of the cost function. Default is 1e-8.
            The optimization process is stopped when dF < ftol * F, and there was an adequate agreement
            between a local quadratic model and the true model in the last step.
        :param xtol: float
            Tolerance for termination by the change of the independent variables. Default is 1e-8.
            The exact condition depends on the method used:
            - For `trf` and `dogbox` : norm(dx) < xtol * (xtol + norm(x))
            - For `lm` : Delta < xtol * norm(xs), where Delta is a trust-region radius and xs is the value
                        of x scaled according to x_scale parameter (see below).
        :param gtol:
            Tolerance for termination by the norm of the gradient. Default is 1e-8. The exact condition
            depends on a method used:
            - For `trf` : norm(g_scaled, ord=np.inf) < gtol,
              where g_scaled is the value of the gradient scaled to account for the presence of the bounds [STIR].
            - For `dogbox` : norm(g_free, ord=np.inf) < gtol,
              where g_free is the gradient with respect to the variables which are not in the optimal state
              on the boundary.
            - For `lm` : the maximum absolute value of the cosine of angles
              between columns of the Jacobian and the residual vector is less than gtol, or the residual vector is zero.
        :param max_nfev: None or int
            Maximum number of function evaluations before the termination. If None (default),
            the value is chosen automatically:
            - For `trf` and `dogbox` : 100 * n.
            - For `lm` : 100 * n if jac is callable and 100 * n * (n + 1) otherwise (because 'lm' counts function
             calls in Jacobian estimation).
        :param x_scale: array_like or 'jac'
            Characteristic scale of each variable. Setting x_scale is equivalent to reformulating the problem
            in scaled variables xs = x / x_scale.
            An alternative view is that the size of a trust region along j-th dimension is proportional to x_scale[j].
            Improved convergence may be achieved by setting x_scale such that a step of a given size along any of the
            scaled variables has a similar effect on the cost function. If set to `jac`,
            the scale is iteratively updated using the inverse norms of the columns of the Jacobian matrix
        :param verbose: {0, 1, 2}
             Level of algorithm`s verbosity:
             - 0 (default) : work silently.
             - 1 : display a termination report.
             - 2 : display progress during iterations (not supported by `lm` method).
        :return: OptimizeResult
        """
        self._initialize()
        res = least_squares(
            self._batch_residual,
            self._x0,
            self._batch_jac,
            bounds=self._bounds,
            method=method,
            ftol=ftol,
            xtol=xtol,
            gtol=gtol,
            x_scale=x_scale,
            loss=self._batch_loss,
            tr_solver="lsmr",
            jac_sparsity=self._jac_sparsity,
            max_nfev=max_nfev,
            verbose=verbose,
        )
        self._write_back_to_variables(res.x)
        return res

    def _batch_residual(self, x):
        """
        batch all residual functions to a single unified one.
        :param x:
        :return:
        """
        y = np.zeros(self._dim_residual, dtype=np.float64)
        for residual_block in self._residual_blocks:
            variables = []
            for col_range in residual_block.col_ranges:
                variables.append(x[col_range[0] : col_range[1]])
            row_range = residual_block.row_range
            y[row_range[0] : row_range[1]] = residual_block.residual_func(*variables)
        return y

    def _batch_jac(self, x):
        """
        batch all jacobian functions to a single unified one.
        :param x:
        :return:
        """
        jacobian_matrix = dok_matrix((self._dim_residual, self._dim_variable), dtype=np.float64)
        for residual_block in self._residual_blocks:
            variables = []
            for col_range in residual_block.col_ranges:
                variables.append(x[col_range[0] : col_range[1]])
            # calculate jacobian matrix at current state
            jac = residual_block.jac_func(*variables)
            # set jacobian matrix to the whole-problem jacobian.
            row_range = residual_block.row_range
            shift = 0
            for col_range in residual_block.col_ranges:
                dim = col_range[1] - col_range[0]
                jacobian_matrix[row_range[0] : row_range[1], col_range[0] : col_range[1]] = jac[:, shift : shift + dim]
                shift += dim

        # mask out jacobian blocks of fixed variables
        for address in self._fixed_variable_address:
            col_range = self._address_col_range_map.get(address)
            if col_range is None:
                continue
            jacobian_matrix[:, col_range[0] : col_range[1]] = 0

        return jacobian_matrix

    def _batch_loss(self, z):
        """
        batch all loss functions to a single unified one.
        :param z: z = f(x)**2
        :return: an array_like with shape (3, m) where row 0 contains function values,
        row 1 contains first derivatives and row 2 contains second derivatives.
        """
        if z.shape[0] != self._dim_residual:
            msg = f"Batch loss error, {z.shape[0]} != {self._dim_residual}"
            raise ValueError(msg)
        loss = np.zeros((3, z.shape[0]), dtype=np.float64)
        for residual_block in self._residual_blocks:
            row_range = residual_block.row_range
            loss[:, row_range[0] : row_range[1]] = residual_block.loss_func(z[row_range[0] : row_range[1]])
        return loss

    def _initialize(self):
        # set initial state
        self._x0 = np.zeros(self._dim_variable, dtype=np.float64)
        for col_range, x0 in self._col_range_variable_map.items():
            self._x0[col_range[0] : col_range[1]] = x0

        # set state bounds
        self._bounds = [np.empty(self._x0.shape, dtype=np.float64), np.empty(self._x0.shape, dtype=np.float64)]
        self._bounds[0][:] = -np.inf
        self._bounds[1][:] = np.inf
        for address, bound in self._address_bounds_map.items():
            col_range = self._address_col_range_map[address]
            self._bounds[0][col_range[0] : col_range[1]] = bound[0]
            self._bounds[1][col_range[0] : col_range[1]] = bound[1]

        # set jacobian sparsity for the whole problem
        self._jac_sparsity = dok_matrix((self._dim_residual, self._dim_variable), dtype=int)
        for residual_block in self._residual_blocks:
            if residual_block.jac_sparsity is None:
                jac_sparsity = np.ones((residual_block.dim_residual, residual_block.dim_variable), dtype=int)
            else:
                jac_sparsity = residual_block.jac_sparsity

            row_range = residual_block.row_range
            shift = 0
            for col_range in residual_block.col_ranges:
                dim = col_range[1] - col_range[0]
                self._jac_sparsity[row_range[0] : row_range[1], col_range[0] : col_range[1]] = jac_sparsity[
                    :, shift : shift + dim
                ]
                shift += dim

        # mask out jacobian blocks of fixed variables
        for address in self._fixed_variable_address:
            col_range = self._address_col_range_map.get(address)
            if col_range is None:
                continue
            self._jac_sparsity[:, col_range[0] : col_range[1]] = 0

    def _write_back_to_variables(self, x):
        for col_range, variable in self._col_range_variable_map.items():
            variable[:] = x[col_range[0] : col_range[1]]
