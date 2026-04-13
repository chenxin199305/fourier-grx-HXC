import numpy
import torch


def radian_transmatrix(alpha, a, d, theta):
    T = numpy.matrix(
        [
            [
                numpy.cos(theta),
                -numpy.sin(theta) * numpy.cos(alpha),
                numpy.sin(theta) * numpy.sin(alpha),
                a * numpy.cos(theta),
            ],
            [
                numpy.sin(theta),
                numpy.cos(theta) * numpy.cos(alpha),
                -numpy.cos(theta) * numpy.sin(alpha),
                a * numpy.sin(theta),
            ],
            [0, numpy.sin(alpha), numpy.cos(alpha), d],
            [0, 0, 0, 1],
        ]
    )

    return T


def degree_transmatrix(alpha, a, d, theta):
    T = radian_transmatrix(
        numpy.radians(alpha),
        a,
        d,
        numpy.radians(theta),
    )

    return T


def radian_rpy_to_transmatrix(rpy):
    R = numpy.matrix(
        [
            [
                numpy.cos(rpy[2]) * numpy.cos(rpy[1]),
                numpy.cos(rpy[2]) * numpy.sin(rpy[1]) * numpy.sin(rpy[0]) - numpy.sin(rpy[2]) * numpy.cos(rpy[0]),
                numpy.cos(rpy[2]) * numpy.sin(rpy[1]) * numpy.cos(rpy[0]) + numpy.sin(rpy[2]) * numpy.sin(rpy[0]),
            ],
            [
                numpy.sin(rpy[2]) * numpy.cos(rpy[1]),
                numpy.sin(rpy[2]) * numpy.sin(rpy[1]) * numpy.sin(rpy[0]) + numpy.cos(rpy[2]) * numpy.cos(rpy[0]),
                numpy.sin(rpy[2]) * numpy.sin(rpy[1]) * numpy.cos(rpy[0]) - numpy.cos(rpy[2]) * numpy.sin(rpy[0]),
            ],
            [
                -numpy.sin(rpy[1]),
                numpy.cos(rpy[1]) * numpy.sin(rpy[0]),
                numpy.cos(rpy[1]) * numpy.cos(rpy[0]),
            ],
        ]
    )

    return R


def degree_rpy_to_transmatrix(rpy):
    rpy = numpy.radians(rpy)
    R = radian_rpy_to_transmatrix(rpy)

    return R


def radian_rpy_to_quaternion(rpy):
    R = radian_rpy_to_transmatrix(rpy)

    T = numpy.array(
        [
            [
                R[0, 0],
                R[0, 1],
                R[0, 2],
                0,
            ],
            [
                R[1, 0],
                R[1, 1],
                R[1, 2],
                0,
            ],
            [
                R[2, 0],
                R[2, 1],
                R[2, 2],
                0,
            ],
            [
                0,
                0,
                0,
                1,
            ],
        ]
    )

    Q = transmatrix_to_quaternion(T)

    return Q


def degree_rpy_to_quaternion(rpy):
    rpy = numpy.radians(rpy)
    Q = radian_rpy_to_quaternion(rpy)

    return Q


def radian_xyz_to_transmatrix(xyz):
    T = numpy.matrix(
        [
            [1, 0, 0, xyz[0]],
            [0, 1, 0, xyz[1]],
            [0, 0, 1, xyz[2]],
            [0, 0, 0, 1]
        ]
    )

    return T


def degree_xyz_to_transmatrix(xyz):
    xyz = numpy.radians(xyz)
    T = radian_xyz_to_transmatrix(xyz)

    return T


def radian_transmatrix_to_xyz(T):
    xyz = numpy.array(
        [
            T[0, 3],
            T[1, 3],
            T[2, 3]
        ]
    )

    return xyz


def degree_transmatrix_to_xyz(T):
    xyz = radian_transmatrix_to_xyz(T)
    xyz = numpy.degrees(xyz)

    return xyz


def radian_transmatrix_to_rpy(T):
    R = T[0:3, 0:3]
    rpy = numpy.array(
        [
            numpy.arctan2(R[2, 1], R[2, 2]),
            numpy.arctan2(-R[2, 0], numpy.sqrt(R[2, 1] * R[2, 1] + R[2, 2] * R[2, 2])),
            numpy.arctan2(R[1, 0], R[0, 0]),
        ]
    )

    return rpy


def degree_transmatrix_to_rpy(T):
    rpy = radian_transmatrix_to_rpy(T)
    rpy = numpy.degrees(rpy)

    return rpy


def transmatrix_to_quaternion(T):
    R = T[0:3, 0:3]
    qw = numpy.sqrt(1 + R[0, 0] + R[1, 1] + R[2, 2]) / 2
    qx = (R[2, 1] - R[1, 2]) / (4 * qw)
    qy = (R[0, 2] - R[2, 0]) / (4 * qw)
    qz = (R[1, 0] - R[0, 1]) / (4 * qw)
    q = numpy.array([qx, qy, qz, qw])

    return q


def quaternion_to_transmatrix(q):
    qw = q[3]
    qx = q[0]
    qy = q[1]
    qz = q[2]
    T = numpy.matrix(
        [
            [
                1 - 2 * qy * qy - 2 * qz * qz,
                2 * qx * qy - 2 * qz * qw,
                2 * qx * qz + 2 * qy * qw,
                0,
            ],
            [
                2 * qx * qy + 2 * qz * qw,
                1 - 2 * qx * qx - 2 * qz * qz,
                2 * qy * qz - 2 * qx * qw,
                0,
            ],
            [
                2 * qx * qz - 2 * qy * qw,
                2 * qy * qz + 2 * qx * qw,
                1 - 2 * qx * qx - 2 * qy * qy,
                0,
            ],
            [0, 0, 0, 1],
        ]
    )
    return T


def radian_transmatrix_to_axisangle(T):
    R = T[0:3, 0:3]
    theta = numpy.arccos((numpy.trace(R) - 1) / 2)
    if theta == 0:
        axis = numpy.array([0, 0, 1])
    else:
        axis = numpy.array(
            [
                (R[2, 1] - R[1, 2]) / (2 * numpy.sin(theta)),
                (R[0, 2] - R[2, 0]) / (2 * numpy.sin(theta)),
                (R[1, 0] - R[0, 1]) / (2 * numpy.sin(theta)),
            ]
        )

    return axis, theta


def degree_transmatrix_to_axisangle(T):
    axis, theta = radian_transmatrix_to_axisangle(T)
    theta = numpy.degrees(theta)

    return axis, theta


def radian_axisangle_to_transmatrix(axis, theta):
    T = numpy.matrix(
        [
            [
                numpy.cos(theta) + axis[0] * axis[0] * (1 - numpy.cos(theta)),
                axis[0] * axis[1] * (1 - numpy.cos(theta)) - axis[2] * numpy.sin(theta),
                axis[0] * axis[2] * (1 - numpy.cos(theta)) + axis[1] * numpy.sin(theta),
                0,
            ],
            [
                axis[1] * axis[0] * (1 - numpy.cos(theta)) + axis[2] * numpy.sin(theta),
                numpy.cos(theta) + axis[1] * axis[1] * (1 - numpy.cos(theta)),
                axis[1] * axis[2] * (1 - numpy.cos(theta)) - axis[0] * numpy.sin(theta),
                0,
            ],
            [
                axis[2] * axis[0] * (1 - numpy.cos(theta)) - axis[1] * numpy.sin(theta),
                axis[2] * axis[1] * (1 - numpy.cos(theta)) + axis[0] * numpy.sin(theta),
                numpy.cos(theta) + axis[2] * axis[2] * (1 - numpy.cos(theta)),
                0,
            ],
            [0, 0, 0, 1],
        ]
    )

    return T


def degree_axisangle_to_transmatrix(axis, theta):
    theta = numpy.radians(theta)
    T = radian_axisangle_to_transmatrix(axis, theta)

    return T


def radian_transmatrix_to_homogeneous(T):
    h = numpy.array(
        [
            T[0, 0],
            T[0, 1],
            T[0, 2],
            T[1, 0],
            T[1, 1],
            T[1, 2],
            T[2, 0],
            T[2, 1],
            T[2, 2],
            T[0, 3],
            T[1, 3],
            T[2, 3],
        ]
    )
    return h


def degree_transmatrix_to_homogeneous(T):
    T = numpy.radians(T)
    h = radian_transmatrix_to_homogeneous(T)
    return h


def radian_homogeneous_to_transmatrix(h):
    T = numpy.matrix(
        [
            [h[0], h[1], h[2], h[9]],
            [h[3], h[4], h[5], h[10]],
            [h[6], h[7], h[8], h[11]],
            [0, 0, 0, 1],
        ]
    )
    return T


def degree_homogeneous_to_transmatrix(h):
    h = numpy.radians(h)
    T = radian_homogeneous_to_transmatrix(h)
    return numpy.degrees(T)


def radian_rp_to_horizontal_sextant_angle(rp):
    """Converts a roll-pitch vector to a horizontal sextant angle.

    Args:
        rp: A roll-pitch vector.

    Returns:
        The horizontal sextant angle in radians.
    """
    return numpy.arccos(numpy.cos(rp[0]) * numpy.cos(rp[1]))


def degree_rp_to_horizontal_sextant_angle(rp):
    """Converts a roll-pitch vector to a horizontal sextant angle.

    Args:
        rp: A roll-pitch vector.

    Returns:
        The horizontal sextant angle in degrees.
    """
    return numpy.degrees(radian_rp_to_horizontal_sextant_angle(numpy.radians(rp)))


def quat_rotate_inverse(q, v):
    """
    Rotate a vector by the inverse of a quaternion.

    :param q: A quaternion in the form of [x, y, z, w] in shape of [4].
    :param v: A vector in the form of [x, y, z] in shape of [3].
    :return: The rotated vector in shape of [1, 3].
    """
    q_w = q[-1]
    q_vec = q[:3]
    a = v * (2.0 * q_w ** 2 - 1.0)
    b = numpy.cross(q_vec, v) * q_w * 2.0
    c = q_vec * numpy.matmul(q_vec.reshape(1, 3), v.reshape(3, 1)) * 2.0
    return a - b + c


# def torch_quat_rotate_inverse(q, v):
#     shape = q.shape
#     q_w = q[:, -1]
#     q_vec = q[:, :3]
#     a = v * (2.0 * q_w ** 2 - 1.0).unsqueeze(-1)
#     b = torch.cross(q_vec, v, dim=-1) * q_w.unsqueeze(-1) * 2.0
#     c = q_vec * torch.bmm(q_vec.view(shape[0], 1, 3), v.view(shape[0], 3, 1)).squeeze(-1) * 2.0
#     return a - b + c


def torch_quat_mul(a, b):
    assert a.shape == b.shape
    shape = a.shape
    a = a.reshape(-1, 4)
    b = b.reshape(-1, 4)

    x1, y1, z1, w1 = a[:, 0], a[:, 1], a[:, 2], a[:, 3]
    x2, y2, z2, w2 = b[:, 0], b[:, 1], b[:, 2], b[:, 3]
    ww = (z1 + x1) * (x2 + y2)
    yy = (w1 - y1) * (w2 + z2)
    zz = (w1 + y1) * (w2 - z2)
    xx = ww + yy + zz
    qq = 0.5 * (xx + (z1 - x1) * (x2 - y2))
    w = qq - ww + (z1 - y1) * (y2 - z2)
    x = qq - xx + (x1 + w1) * (x2 + w2)
    y = qq - yy + (w1 - x1) * (y2 + z2)
    z = qq - zz + (z1 + y1) * (w2 - x2)

    quat = torch.stack([x, y, z, w], dim=-1).view(shape)

    return quat


def torch_quat_apply(a, b):
    """
    Apply a quaternion rotation to a vector.

    :param a: A quaternion tensor in the form of [x, y, z, w] in shape of [N, 4].
    :param b: A vector tensor in the form of [x, y, z] in shape of [N, 3].
    :return: The rotated vector tensor in shape of [N, 3].
    """
    q_w = a[:, -1:]
    q_vec = a[:, :3]
    t = torch.cross(q_vec, b, dim=-1) * 2.0
    return b + q_w * t + torch.cross(q_vec, t, dim=-1)


def torch_quat_conjugate(a):
    shape = a.shape
    a = a.reshape(-1, 4)
    return torch.cat((-a[:, :3], a[:, -1:]), dim=-1).view(shape)


def torch_quat_rotate_inverse(q, v):
    """
    Rotate a vector (tensor) by the inverse of a quaternion (tensor).

    :param q: A quaternion tensor in the form of [x, y, z, w] in shape of [N, 4].
    :param v: A vector tensor in the form of [x, y, z] in shape of [N, 3].
    :return: The rotated vector tensor in shape of [N, 3].
    """
    q_w = q[:, -1:]
    q_vec = q[:, :3]

    # Compute the dot product of q_vec and v
    q_vec_dot_v = torch.bmm(q_vec.view(-1, 1, 3), v.view(-1, 3, 1)).squeeze(-1)

    # Compute the cross product of q_vec and v
    q_vec_cross_v = torch.cross(q_vec, v, dim=-1)

    # Compute the rotated vector
    a = v * (2.0 * q_w ** 2 - 1.0)
    b = q_vec_cross_v * q_w * 2.0
    c = q_vec * q_vec_dot_v * 2.0

    return a - b + c


def normalize(x, eps: float = 1e-9):
    return x / x.norm(p=2, dim=-1).clamp(min=eps, max=None).unsqueeze(-1)


def quat_unit(a):
    return normalize(a)


def quat_from_angle_axis(angle, axis):
    theta = (angle / 2).unsqueeze(-1)
    xyz = normalize(axis) * theta.sin()
    w = theta.cos()
    return quat_unit(numpy.cat([xyz, w], dim=-1))


def to_torch(x, dtype=torch.float, device='cpu', requires_grad=False):
    return torch.tensor(x, dtype=dtype, device=device, requires_grad=requires_grad)


if __name__ == "__main__":
    q = torch.Tensor([[0, 0, 0, 1]])
    v = torch.Tensor([[0, 0, -1]])

    result = torch_quat_rotate_inverse(q, v)
    print("result = ", result)

    q = numpy.array([0, 0, 0, 1])
    v = numpy.array([0, 0, -1])

    result = quat_rotate_inverse(q, v)
    print("result = ", result)
