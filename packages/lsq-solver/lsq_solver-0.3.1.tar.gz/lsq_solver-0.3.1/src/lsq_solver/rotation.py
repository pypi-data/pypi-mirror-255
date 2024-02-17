import numpy as np

ROTATION_VEC_SIZE = 3


def rotation_matrix(rvec: np.ndarray) -> np.ndarray:
    """Return the rotation matrix associated with counterclockwise rotation about the given rotation vector."""
    if len(rvec) != ROTATION_VEC_SIZE:
        msg = f"rvec size should be 3, got {rvec.size}"
        raise ValueError(msg)
    theta = np.linalg.norm(rvec)
    axis = np.divide(rvec, theta)
    a = np.cos(theta / 2.0)
    b, c, d = -axis * np.sin(theta / 2.0)
    aa, bb, cc, dd = a * a, b * b, c * c, d * d
    bc, ad, ac, ab, bd, cd = b * c, a * d, a * c, a * b, b * d, c * d
    return np.array(
        [
            [aa + bb - cc - dd, 2 * (bc + ad), 2 * (bd - ac)],
            [2 * (bc - ad), aa + cc - bb - dd, 2 * (cd + ab)],
            [2 * (bd + ac), 2 * (cd - ab), aa + dd - bb - cc],
        ]
    )
