import numpy as np
from scipy.spatial.transform import Rotation as R


def pose_to_transformation_matrix(pose):
    x, y, z, qw, qx, qy, qz = pose

    norm = np.sqrt(qw * qw + qx * qx + qy * qy + qz * qz)
    qw /= norm
    qx /= norm
    qy /= norm
    qz /= norm

    xx = qx * qx
    xy = qx * qy
    xz = qx * qz
    xw = qx * qw

    yy = qy * qy
    yz = qy * qz
    yw = qy * qw

    zz = qz * qz
    zw = qz * qw

    rotation_matrix = np.array([
        [1 - 2 * (yy + zz), 2 * (xy - zw), 2 * (xz + yw)],
        [2 * (xy + zw), 1 - 2 * (xx + zz), 2 * (yz - xw)],
        [2 * (xz - yw), 2 * (yz + xw), 1 - 2 * (xx + yy)]
    ])

    transformation_matrix = np.eye(4)
    transformation_matrix[:3, :3] = rotation_matrix
    transformation_matrix[:3, 3] = [x, y, z]

    return transformation_matrix


def transformation_matrix_to_pose(transform):
    assert transform.shape == (4, 4), "The transformation must be a 4x4 matrix."

    position = transform[:3, 3]

    rotation_matrix = transform[:3, :3]

    rotation = R.from_matrix(rotation_matrix)
    quaternion = rotation.as_quat()

    pose = [position[0], position[1], position[2], quaternion[3], quaternion[0], quaternion[1], quaternion[2]]

    return pose  # x y z qw qx qy qz
