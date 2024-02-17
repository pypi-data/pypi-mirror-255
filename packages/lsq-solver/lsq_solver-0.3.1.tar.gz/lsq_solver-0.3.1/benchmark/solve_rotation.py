from functools import partial
from time import perf_counter

import numpy as np
from num_dual import Dual64, first_derivative, gradient, jacobian, second_partial_derivative
from scipy.spatial.transform import Rotation

from lsq_solver import LeastSquaresProblem
from lsq_solver.auto_diff import (
    AUTO_DIFF_NAMES,
    diff_2point,
    diff_3point,
    diff_auto,
    diff_auto_multiple_variable,
    diff_dual,
)
from lsq_solver.rotation import rotation_matrix


def cost(p3ds: np.ndarray, p2ds: np.ndarray, rvec: np.ndarray) -> np.ndarray:
    p3dd = rotation_matrix(rvec) @ p3ds
    return (p3dd[:2, :] / p3dd[2:, :] - p2ds).flatten()


if __name__ == "__main__":
    p_num = 1000
    p3ds_gt = (np.random.random((p_num, 3)) * 100 + np.array([0, 0, 1])).T
    rvec_gt = np.random.random(3)
    print("gt", rvec_gt)
    rmat_gt = Rotation.from_rotvec(rvec_gt).as_matrix()
    p3ds_gt_r = rmat_gt @ p3ds_gt
    p2ds_gt = p3ds_gt_r[:2, :] / p3ds_gt_r[2:, :]

    rvec = rvec_gt + np.random.random(3) / 100
    rmat = Rotation.from_rotvec(rvec).as_matrix()
    p3ds_r = rmat @ p3ds_gt
    name_time = []
    for n in sorted(list(AUTO_DIFF_NAMES)):
        problem = LeastSquaresProblem()
        cc = partial(cost, p3ds_gt, p2ds_gt)
        rvec_init = rvec.copy()
        problem.add_residual_block(p3ds_r.shape[1] * 2, cc, rvec_init, jac_func=n)
        print("init  ", rvec_init)
        s = perf_counter()
        problem.solve(verbose=2)
        t = perf_counter() - s
        name_time.append((n, t))
        print("result", rvec_init)
    for n, t in name_time:
        print(f"{n}\t{t:.6f}s")
