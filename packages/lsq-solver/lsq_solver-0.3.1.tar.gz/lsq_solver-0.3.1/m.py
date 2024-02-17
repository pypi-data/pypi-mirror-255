# from jaxopt import GaussNewton
# # import numpy as np
# import jax.numpy as np
# def rosenbrock(x):
#     return np.array([10 * (x[1] - x[0]**2), (1 - x[0])])

# gn = GaussNewton(residual_fun=rosenbrock)
# x_init = np.array([345, 111.0], dtype=np.float32)
# gn_sol = gn.run([900.0, -2223.0]).params
# print(gn_sol)
# import jax.numpy as jnp
# from jax import grad, jit, vmap, jacobian
# from functools import partial

# import numpy as np
# from scipy.spatial.transform import Rotation

from lsq_solver import LeastSquaresProblem
from lsq_solver.auto_diff import AUTO_DIFF_NAMES
from lsq_solver.rotation import rotation_matrix


# def cost(p3ds: np.ndarray, p2ds: np.ndarray, rvec: np.ndarray) -> np.ndarray:
#     p3dd = rotation_matrix(rvec) @ p3ds
#     return (p3dd[:2, :] / p3dd[2:, :] - p2ds).flatten()

# def f(x, y):
#     return [2*x[0], y[0]*y[0], x[1]+y[1], y[2]**3]

# def main():
#     j = jit(jacobian(f, 0))
#     print(j)
#     x = np.array([1.0, 2])
#     y = np.array([3.0, 4, 5])
#     print(np.vstack(j(x, y)))

#     exit()
#     auto_diff_name = 'dual'

#     p3ds_gt = (np.random.random((100, 3)) * 100 + np.array([0, 0, 1])).T
#     rvec_gt = np.random.random(3)
#     rmat_gt = Rotation.from_rotvec(rvec_gt).as_matrix()
#     p3ds_gt_r = rmat_gt @ p3ds_gt
#     p2ds_gt = p3ds_gt_r[:2, :] / p3ds_gt_r[2:, :]

#     rvec = rvec_gt + np.random.random(3) / 100
#     rmat = Rotation.from_rotvec(rvec).as_matrix()
#     p3ds_r = rmat @ p3ds_gt
#     problem = LeastSquaresProblem()
#     cc = partial(cost, p3ds_gt, p2ds_gt)
#     problem.add_residual_block(p3ds_r.shape[1] * 2, cc, rvec, jac_func=auto_diff_name)
#     problem.solve()
#     assert np.allclose(rvec_gt, rvec)

# if __name__ == '__main__':
#     main()
