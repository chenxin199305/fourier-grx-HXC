import numpy

from fourier_core.predefine import *
import fourier_core.tool.pd_conversion as pd_conversion

from fourier_grx.predefine import *
from fourier_grx.tool.fi_tool_logger import Logger


def GR1T1_pd_dict() -> dict:
    pd_dict = {
        "left_hip_roll_joint": [ActuatorFIFSAType.FSA_TYPE_802030, 251.625, 14.72],
        "left_hip_yaw_joint": [ActuatorFIFSAType.FSA_TYPE_601750, 362.52, 10.0833],
        "left_hip_pitch_joint": [ActuatorFIFSAType.FSA_TYPE_1307E, 200, 11],
        "left_knee_pitch_joint": [ActuatorFIFSAType.FSA_TYPE_1307E, 200, 11],
        "left_ankle_pitch_joint": [ActuatorFIFSAType.FSA_TYPE_36B36E, 10.98, 0.599],
        "left_ankle_roll_joint": [ActuatorFIFSAType.FSA_TYPE_36B36E, 10.98, 0.599],
        "right_hip_roll_joint": [ActuatorFIFSAType.FSA_TYPE_802030, 251.625, 14.72],
        "right_hip_yaw_joint": [ActuatorFIFSAType.FSA_TYPE_601750, 362.52, 10.0833],
        "right_hip_pitch_joint": [ActuatorFIFSAType.FSA_TYPE_1307E, 200, 11],
        "right_knee_pitch_joint": [ActuatorFIFSAType.FSA_TYPE_1307E, 200, 11],
        "right_ankle_pitch_joint": [ActuatorFIFSAType.FSA_TYPE_36B36E, 10.98, 0.599],
        "right_ankle_roll_joint": [ActuatorFIFSAType.FSA_TYPE_36B36E, 10.98, 0.599],
        "waist_yaw_joint": [ActuatorFIFSAType.FSA_TYPE_601750, 362.52, 10.0833],
        "waist_pitch_joint": [ActuatorFIFSAType.FSA_TYPE_601750, 362.52, 10.0833],
        "waist_roll_joint": [ActuatorFIFSAType.FSA_TYPE_601750, 362.52, 10.0833],
        "head_yaw_joint": [ActuatorFIFSAType.FSA_TYPE_3611100, 112.06, 3.1],
        "head_pitch_joint": [ActuatorFIFSAType.FSA_TYPE_3611100, 112.06, 3.1],
        "head_roll_joint": [ActuatorFIFSAType.FSA_TYPE_3611100, 112.06, 3.1],
        "left_shoulder_pitch_joint": [ActuatorFIFSAType.FSA_TYPE_361480, 92.85, 2.575],
        "left_shoulder_roll_joint": [ActuatorFIFSAType.FSA_TYPE_361480, 92.85, 2.575],
        "left_shoulder_yaw_joint": [ActuatorFIFSAType.FSA_TYPE_3611100, 112.06, 3.1],
        "left_elbow_pitch_joint": [ActuatorFIFSAType.FSA_TYPE_3611100, 112.06, 3.1],
        "right_shoulder_pitch_joint": [ActuatorFIFSAType.FSA_TYPE_361480, 92.85, 2.575],
        "right_shoulder_roll_joint": [ActuatorFIFSAType.FSA_TYPE_361480, 92.85, 2.575],
        "right_shoulder_yaw_joint": [ActuatorFIFSAType.FSA_TYPE_3611100, 112.06, 3.1],
        "right_elbow_pitch_joint": [ActuatorFIFSAType.FSA_TYPE_3611100, 112.06, 3.1],
    }

    return pd_dict


def GR1T1V2_pd_dict() -> dict:
    pd_dict = {
        "left_hip_roll_joint": [ActuatorFIFSAType.FSA_TYPE_802029, 251.625, 14.72],
        "left_hip_yaw_joint": [ActuatorFIFSAType.FSA_TYPE_601750, 362.52, 10.0833],
        "left_hip_pitch_joint": [ActuatorFIFSAType.FSA_TYPE_1307E, 200, 11],
        "left_knee_pitch_joint": [ActuatorFIFSAType.FSA_TYPE_1307E, 200, 11],
        "left_ankle_pitch_joint": [ActuatorFIFSAType.FSA_TYPE_36B36E, 10.98, 0.6],
        "left_ankle_roll_joint": [ActuatorFIFSAType.FSA_TYPE_36B36E, 10.98, 0.6],
        "right_hip_roll_joint": [ActuatorFIFSAType.FSA_TYPE_802029, 251.625, 14.72],
        "right_hip_yaw_joint": [ActuatorFIFSAType.FSA_TYPE_601750, 362.52, 10.0833],
        "right_hip_pitch_joint": [ActuatorFIFSAType.FSA_TYPE_1307E, 200, 11],
        "right_knee_pitch_joint": [ActuatorFIFSAType.FSA_TYPE_1307E, 200, 11],
        "right_ankle_pitch_joint": [ActuatorFIFSAType.FSA_TYPE_36B36E, 10.98, 0.6],
        "right_ankle_roll_joint": [ActuatorFIFSAType.FSA_TYPE_36B36E, 10.98, 0.6],
        "waist_yaw_joint": [ActuatorFIFSAType.FSA_TYPE_601750, 362.52, 10.0833],
        "waist_pitch_joint": [ActuatorFIFSAType.FSA_TYPE_601750, 362.52, 10.0833],
        "waist_roll_joint": [ActuatorFIFSAType.FSA_TYPE_601750, 362.52, 10.0833],
        "left_shoulder_pitch_joint": [ActuatorFIFSAType.FSA_TYPE_361480, 92.85, 2.575],
        "left_shoulder_roll_joint": [ActuatorFIFSAType.FSA_TYPE_361480, 92.85, 2.575],
        "left_shoulder_yaw_joint": [ActuatorFIFSAType.FSA_TYPE_3611100, 112.06, 3.1],
        "left_elbow_pitch_joint": [ActuatorFIFSAType.FSA_TYPE_3611100, 112.06, 3.1],
        "right_shoulder_pitch_joint": [ActuatorFIFSAType.FSA_TYPE_361480, 92.85, 2.575],
        "right_shoulder_roll_joint": [ActuatorFIFSAType.FSA_TYPE_361480, 92.85, 2.575],
        "right_shoulder_yaw_joint": [ActuatorFIFSAType.FSA_TYPE_3611100, 112.06, 3.1],
        "right_elbow_pitch_joint": [ActuatorFIFSAType.FSA_TYPE_3611100, 112.06, 3.1],
    }

    return pd_dict


def GR1T1V3_pd_dict() -> dict:
    pd_dict = {
        "left_hip_roll_joint": [ActuatorFIFSAType.FSA_TYPE_802029, 251.625, 14.72],
        "left_hip_yaw_joint": [ActuatorFIFSAType.FSA_TYPE_601750, 362.52, 10.0833],
        "left_hip_pitch_joint": [ActuatorFIFSAType.FSA_TYPE_13014E, 200, 11],
        "left_knee_pitch_joint": [ActuatorFIFSAType.FSA_TYPE_13014E, 200, 11],
        "left_ankle_pitch_joint": [ActuatorFIFSAType.FSA_TYPE_36B36E, 10.98, 0.6],
        "left_ankle_roll_joint": [ActuatorFIFSAType.FSA_TYPE_36B36E, 10.98, 0.6],
        "right_hip_roll_joint": [ActuatorFIFSAType.FSA_TYPE_802029, 251.625, 14.72],
        "right_hip_yaw_joint": [ActuatorFIFSAType.FSA_TYPE_601750, 362.52, 10.0833],
        "right_hip_pitch_joint": [ActuatorFIFSAType.FSA_TYPE_13014E, 200, 11],
        "right_knee_pitch_joint": [ActuatorFIFSAType.FSA_TYPE_13014E, 200, 11],
        "right_ankle_pitch_joint": [ActuatorFIFSAType.FSA_TYPE_36B36E, 10.98, 0.6],
        "right_ankle_roll_joint": [ActuatorFIFSAType.FSA_TYPE_36B36E, 10.98, 0.6],
        "waist_yaw_joint": [ActuatorFIFSAType.FSA_TYPE_601750, 362.52, 10.0833],
        "waist_pitch_joint": [ActuatorFIFSAType.FSA_TYPE_601750, 362.52, 10.0833],
        "waist_roll_joint": [ActuatorFIFSAType.FSA_TYPE_601750, 362.52, 10.0833],
        "left_shoulder_pitch_joint": [ActuatorFIFSAType.FSA_TYPE_361480, 92.85, 2.575],
        "left_shoulder_roll_joint": [ActuatorFIFSAType.FSA_TYPE_361480, 92.85, 2.575],
        "left_shoulder_yaw_joint": [ActuatorFIFSAType.FSA_TYPE_3611100, 112.06, 3.1],
        "left_elbow_pitch_joint": [ActuatorFIFSAType.FSA_TYPE_3611100, 112.06, 3.1],
        "right_shoulder_pitch_joint": [ActuatorFIFSAType.FSA_TYPE_361480, 92.85, 2.575],
        "right_shoulder_roll_joint": [ActuatorFIFSAType.FSA_TYPE_361480, 92.85, 2.575],
        "right_shoulder_yaw_joint": [ActuatorFIFSAType.FSA_TYPE_3611100, 112.06, 3.1],
        "right_elbow_pitch_joint": [ActuatorFIFSAType.FSA_TYPE_3611100, 112.06, 3.1],
    }

    return pd_dict


def GR1T2_pd_dict() -> dict:
    pd_dict = {
        "left_hip_roll_joint": [ActuatorFIFSAType.FSA_TYPE_802030, 251.625, 14.72],
        "left_hip_yaw_joint": [ActuatorFIFSAType.FSA_TYPE_601750, 362.52, 10.0833],
        "left_hip_pitch_joint": [ActuatorFIFSAType.FSA_TYPE_1307E, 200, 11],
        "left_knee_pitch_joint": [ActuatorFIFSAType.FSA_TYPE_1307E, 200, 11],
        "left_ankle_pitch_joint": [ActuatorFIFSAType.FSA_TYPE_36B36E, 10.98, 0.5991],
        "left_ankle_roll_joint": [ActuatorFIFSAType.FSA_TYPE_36B36E, 10.98, 0.5991],
        "right_hip_roll_joint": [ActuatorFIFSAType.FSA_TYPE_802030, 251.625, 14.72],
        "right_hip_yaw_joint": [ActuatorFIFSAType.FSA_TYPE_601750, 362.52, 10.0833],
        "right_hip_pitch_joint": [ActuatorFIFSAType.FSA_TYPE_1307E, 200, 11],
        "right_knee_pitch_joint": [ActuatorFIFSAType.FSA_TYPE_1307E, 200, 11],
        "right_ankle_pitch_joint": [ActuatorFIFSAType.FSA_TYPE_36B36E, 10.98, 0.5991],
        "right_ankle_roll_joint": [ActuatorFIFSAType.FSA_TYPE_36B36E, 10.98, 0.5991],
        "waist_yaw_joint": [ActuatorFIFSAType.FSA_TYPE_601750, 362.52, 10.0833],
        "waist_pitch_joint": [ActuatorFIFSAType.FSA_TYPE_601750, 362.52, 10.0833],
        "waist_roll_joint": [ActuatorFIFSAType.FSA_TYPE_601750, 362.52, 10.0833],
        "head_roll_joint": [ActuatorFIFSAType.FSA_TYPE_250830, 10, 1],
        "head_pitch_joint": [ActuatorFIFSAType.FSA_TYPE_250830, 10, 1],
        "head_yaw_joint": [ActuatorFIFSAType.FSA_TYPE_250830, 10, 1],
        "left_shoulder_pitch_joint": [ActuatorFIFSAType.FSA_TYPE_361480, 92.85, 2.575],
        "left_shoulder_roll_joint": [ActuatorFIFSAType.FSA_TYPE_361480, 92.85, 2.575],
        "left_shoulder_yaw_joint": [ActuatorFIFSAType.FSA_TYPE_3611100, 112.06, 3.1],
        "left_elbow_pitch_joint": [ActuatorFIFSAType.FSA_TYPE_3611100, 112.06, 3.1],
        "left_wrist_yaw_joint": [ActuatorFIFSAType.FSA_TYPE_3611100, 10, 1],
        "left_wrist_roll_joint": [ActuatorFIFSAType.FSA_TYPE_250830, 10, 1],
        "left_wrist_pitch_joint": [ActuatorFIFSAType.FSA_TYPE_250830, 10, 1],
        "right_shoulder_pitch_joint": [ActuatorFIFSAType.FSA_TYPE_361480, 92.85, 2.575],
        "right_shoulder_roll_joint": [ActuatorFIFSAType.FSA_TYPE_361480, 92.85, 2.575],
        "right_shoulder_yaw_joint": [ActuatorFIFSAType.FSA_TYPE_3611100, 112.06, 3.1],
        "right_elbow_pitch_joint": [ActuatorFIFSAType.FSA_TYPE_3611100, 112.06, 3.1],
        "right_wrist_yaw_joint": [ActuatorFIFSAType.FSA_TYPE_3611100, 10, 1],
        "right_wrist_roll_joint": [ActuatorFIFSAType.FSA_TYPE_250830, 10, 1],
        "right_wrist_pitch_joint": [ActuatorFIFSAType.FSA_TYPE_250830, 10, 1],
    }

    return pd_dict


def GR1T1_low_stiffness_pd_dict() -> dict:
    pd_dict = {
        "left_hip_roll_joint": [ActuatorFIFSAType.FSA_TYPE_802030, 40, 40 / 10 * 1.0],
        "left_hip_yaw_joint": [ActuatorFIFSAType.FSA_TYPE_601750, 45, 45 / 10 * 1.0],
        "left_hip_pitch_joint": [ActuatorFIFSAType.FSA_TYPE_1307E, 130, 130 / 10 * 1.0],
        "left_knee_pitch_joint": [ActuatorFIFSAType.FSA_TYPE_1307E, 130, 130 / 10 * 1.0],
        "left_ankle_pitch_joint": [ActuatorFIFSAType.FSA_TYPE_36B36E, 18, 18 / 10 * 1.0],
        "left_ankle_roll_joint": [ActuatorFIFSAType.FSA_TYPE_36B36E, 18, 18 / 10 * 1.0],
        "right_hip_roll_joint": [ActuatorFIFSAType.FSA_TYPE_802030, 40, 40 / 10 * 1.0],
        "right_hip_yaw_joint": [ActuatorFIFSAType.FSA_TYPE_601750, 45, 45 / 10 * 1.0],
        "right_hip_pitch_joint": [ActuatorFIFSAType.FSA_TYPE_1307E, 130, 130 / 10 * 1.0],
        "right_knee_pitch_joint": [ActuatorFIFSAType.FSA_TYPE_1307E, 130, 130 / 10 * 1.0],
        "right_ankle_pitch_joint": [ActuatorFIFSAType.FSA_TYPE_36B36E, 18, 18 / 10 * 1.0],
        "right_ankle_roll_joint": [ActuatorFIFSAType.FSA_TYPE_36B36E, 18, 18 / 10 * 1.0],
        "waist_yaw_joint": [ActuatorFIFSAType.FSA_TYPE_601750, 45, 45 / 10 * 1.0],
        "waist_pitch_joint": [ActuatorFIFSAType.FSA_TYPE_601750, 45, 45 / 10 * 1.0],
        "waist_roll_joint": [ActuatorFIFSAType.FSA_TYPE_601750, 45, 45 / 10 * 1.0],
        "left_shoulder_pitch_joint": [ActuatorFIFSAType.FSA_TYPE_361480, 30, 30 / 10 * 1.0],
        "left_shoulder_roll_joint": [ActuatorFIFSAType.FSA_TYPE_361480, 30, 30 / 10 * 1.0],
        "left_shoulder_yaw_joint": [ActuatorFIFSAType.FSA_TYPE_3611100, 30, 30 / 10 * 1.0],
        "left_elbow_pitch_joint": [ActuatorFIFSAType.FSA_TYPE_3611100, 30, 30 / 10 * 1.0],
        "right_shoulder_pitch_joint": [ActuatorFIFSAType.FSA_TYPE_361480, 30, 30 / 10 * 1.0],
        "right_shoulder_roll_joint": [ActuatorFIFSAType.FSA_TYPE_361480, 30, 30 / 10 * 1.0],
        "right_shoulder_yaw_joint": [ActuatorFIFSAType.FSA_TYPE_3611100, 30, 30 / 10 * 1.0],
        "right_elbow_pitch_joint": [ActuatorFIFSAType.FSA_TYPE_3611100, 30, 30 / 10 * 1.0],
    }

    return pd_dict


def GR1T1_dic_pd_dict() -> dict:
    pd_dict = {
        "left_hip_roll_joint": [ActuatorFIFSAType.FSA_TYPE_802030, 40, 40 / 10 * 2.5],
        "left_hip_yaw_joint": [ActuatorFIFSAType.FSA_TYPE_601750, 45, 45 / 10 * 7.5],
        "left_hip_pitch_joint": [ActuatorFIFSAType.FSA_TYPE_1307E, 130, 130 / 10 * 2.5],
        "left_knee_pitch_joint": [ActuatorFIFSAType.FSA_TYPE_1307E, 130, 130 / 10 * 2.5],
        "left_ankle_pitch_joint": [ActuatorFIFSAType.FSA_TYPE_36B36E, 18, 18 / 10 * 2.5],
        "left_ankle_roll_joint": [ActuatorFIFSAType.FSA_TYPE_36B36E, 18, 18 / 10 * 2.5],
        "right_hip_roll_joint": [ActuatorFIFSAType.FSA_TYPE_802030, 40, 40 / 10 * 2.5],
        "right_hip_yaw_joint": [ActuatorFIFSAType.FSA_TYPE_601750, 45, 45 / 10 * 7.5],
        "right_hip_pitch_joint": [ActuatorFIFSAType.FSA_TYPE_1307E, 130, 130 / 10 * 2.5],
        "right_knee_pitch_joint": [ActuatorFIFSAType.FSA_TYPE_1307E, 130, 130 / 10 * 2.5],
        "right_ankle_pitch_joint": [ActuatorFIFSAType.FSA_TYPE_36B36E, 18, 18 / 10 * 2.5],
        "right_ankle_roll_joint": [ActuatorFIFSAType.FSA_TYPE_36B36E, 18, 18 / 10 * 2.5],
        "waist_yaw_joint": [ActuatorFIFSAType.FSA_TYPE_601750, 45, 45 / 10 * 7.5],
        "waist_pitch_joint": [ActuatorFIFSAType.FSA_TYPE_601750, 45, 45 / 10 * 7.5],
        "waist_roll_joint": [ActuatorFIFSAType.FSA_TYPE_601750, 45, 45 / 10 * 7.5],
        "left_shoulder_pitch_joint": [ActuatorFIFSAType.FSA_TYPE_361480, 30, 30 / 10 * 7.5],
        "left_shoulder_roll_joint": [ActuatorFIFSAType.FSA_TYPE_361480, 30, 30 / 10 * 7.5],
        "left_shoulder_yaw_joint": [ActuatorFIFSAType.FSA_TYPE_3611100, 30, 30 / 10 * 7.5],
        "left_elbow_pitch_joint": [ActuatorFIFSAType.FSA_TYPE_3611100, 30, 30 / 10 * 7.5],
        "right_shoulder_pitch_joint": [ActuatorFIFSAType.FSA_TYPE_361480, 30, 30 / 10 * 7.5],
        "right_shoulder_roll_joint": [ActuatorFIFSAType.FSA_TYPE_361480, 30, 30 / 10 * 7.5],
        "right_shoulder_yaw_joint": [ActuatorFIFSAType.FSA_TYPE_3611100, 30, 30 / 10 * 7.5],
        "right_elbow_pitch_joint": [ActuatorFIFSAType.FSA_TYPE_3611100, 30, 30 / 10 * 7.5],
    }

    return pd_dict


def GR2T2_dic_pd_dict() -> dict:
    pd_dict = {
        # left leg
        "left_hip_pitch_joint": [ActuatorFIFSAType.FSA_TYPE_10043E, 699.008, 699.008 / 10 * 0.5],
        "left_hip_roll_joint": [ActuatorFIFSAType.FSA_TYPE_8029E, 182.338, 182.338 / 10 * 0.5],
        "left_hip_yaw_joint": [ActuatorFIFSAType.FSA_TYPE_6043E, 103.705, 103.705 / 10 * 0.5],
        "left_knee_pitch_joint": [ActuatorFIFSAType.FSA_TYPE_10043E, 699.008, 699.008 / 10 * 0.5],
        "left_ankle_roll_joint": [ActuatorFIFSAType.FSA_TYPE_4530E, 55.959, 55.959 / 10 * 0.5],
        "left_ankle_pitch_joint": [ActuatorFIFSAType.FSA_TYPE_6043E, 103.705, 103.705 / 10 * 0.5],
        # right leg
        "right_hip_pitch_joint": [ActuatorFIFSAType.FSA_TYPE_10043E, 699.008, 699.008 / 10 * 0.5],
        "right_hip_roll_joint": [ActuatorFIFSAType.FSA_TYPE_8029E, 182.338, 182.338 / 10 * 0.5],
        "right_hip_yaw_joint": [ActuatorFIFSAType.FSA_TYPE_6043E, 103.705, 103.705 / 10 * 0.5],
        "right_knee_pitch_joint": [ActuatorFIFSAType.FSA_TYPE_10043E, 699.008, 699.008 / 10 * 0.5],
        "right_ankle_roll_joint": [ActuatorFIFSAType.FSA_TYPE_4530E, 55.959, 55.959 / 10 * 0.5],
        "right_ankle_pitch_joint": [ActuatorFIFSAType.FSA_TYPE_6043E, 103.705, 103.705 / 10 * 0.5],
        # waist
        "waist_yaw_joint": [ActuatorFIFSAType.FSA_TYPE_601780Z, 142.094, 142.094 / 10 * 0.5],
        # head
        "head_yaw_joint": [ActuatorFIFSAType.FSA_TYPE_250830, 33.232, 33.232 / 10 * 0.5],
        "head_pitch_joint": [ActuatorFIFSAType.FSA_TYPE_250830, 33.232, 33.232 / 10 * 0.5],
        # left arm
        "left_shoulder_pitch_joint": [ActuatorFIFSAType.FSA_TYPE_601780Z, 142.094, 142.094 / 10 * 0.5],
        "left_shoulder_roll_joint": [ActuatorFIFSAType.FSA_TYPE_601780Z, 142.094, 142.094 / 10 * 0.5],
        "left_shoulder_yaw_joint": [ActuatorFIFSAType.FSA_TYPE_45_17_80Z, 81.933, 81.933 / 10 * 0.5],
        "left_elbow_pitch_joint": [ActuatorFIFSAType.FSA_TYPE_45_17_80Z, 81.933, 81.933 / 10 * 0.5],
        "left_wrist_yaw_joint": [ActuatorFIFSAType.FSA_TYPE_36_14_80Z, 33.232, 33.232 / 10 * 0.5],
        "left_wrist_pitch_joint": [ActuatorFIFSAType.FSA_TYPE_36_14_80Z, 33.232, 33.232 / 10 * 0.5],
        "left_wrist_roll_joint": [ActuatorFIFSAType.FSA_TYPE_36_14_80Z, 33.232, 33.232 / 10 * 0.5],
        # right arm
        "right_shoulder_pitch_joint": [ActuatorFIFSAType.FSA_TYPE_601780Z, 142.094, 142.094 / 10 * 0.5],
        "right_shoulder_roll_joint": [ActuatorFIFSAType.FSA_TYPE_601780Z, 142.094, 142.094 / 10 * 0.5],
        "right_shoulder_yaw_joint": [ActuatorFIFSAType.FSA_TYPE_45_17_80Z, 81.933, 81.933 / 10 * 0.5],
        "right_elbow_pitch_joint": [ActuatorFIFSAType.FSA_TYPE_45_17_80Z, 81.933, 81.933 / 10 * 0.5],
        "right_wrist_yaw_joint": [ActuatorFIFSAType.FSA_TYPE_36_14_80Z, 33.232, 33.232 / 10 * 0.5],
        "right_wrist_pitch_joint": [ActuatorFIFSAType.FSA_TYPE_36_14_80Z, 33.232, 33.232 / 10 * 0.5],
        "right_wrist_roll_joint": [ActuatorFIFSAType.FSA_TYPE_36_14_80Z, 33.232, 33.232 / 10 * 0.5],
    }

    return pd_dict


def GR2T3_dic_pd_dict() -> dict:
    pd_dict = {
        # left leg
        "left_hip_pitch_joint": [ActuatorFIFSAType.FSA_TYPE_10043E, 90, 19, ],
        "left_hip_roll_joint": [ActuatorFIFSAType.FSA_TYPE_8029E, 180, 10, ],
        "left_hip_yaw_joint": [ActuatorFIFSAType.FSA_TYPE_6043E, 120, 9, ],
        "left_knee_pitch_joint": [ActuatorFIFSAType.FSA_TYPE_10043E, 90, 19, ],
        "left_ankle_pitch_joint": [ActuatorFIFSAType.FSA_TYPE_4530E, 30, 5, ],
        "left_ankle_roll_joint": [ActuatorFIFSAType.FSA_TYPE_6043E, 60, 3.5, ],
        # right leg
        "right_hip_pitch_joint": [ActuatorFIFSAType.FSA_TYPE_10043E, 90, 19, ],
        "right_hip_roll_joint": [ActuatorFIFSAType.FSA_TYPE_8029E, 180, 10, ],
        "right_hip_yaw_joint": [ActuatorFIFSAType.FSA_TYPE_6043E, 120, 9, ],
        "right_knee_pitch_joint": [ActuatorFIFSAType.FSA_TYPE_10043E, 90, 19, ],
        "right_ankle_pitch_joint": [ActuatorFIFSAType.FSA_TYPE_4530E, 30, 5, ],
        "right_ankle_roll_joint": [ActuatorFIFSAType.FSA_TYPE_6043E, 60, 3.5, ],
        # waist
        "waist_yaw_joint": [ActuatorFIFSAType.FSA_TYPE_601780Z, 20, 7, ],
        # head
        "head_yaw_joint": [ActuatorFIFSAType.FSA_TYPE_250830, 10, 2.5, ],
        "head_pitch_joint": [ActuatorFIFSAType.FSA_TYPE_250830, 10, 2.5, ],
        # left arm
        "left_shoulder_pitch_joint": [ActuatorFIFSAType.FSA_TYPE_601780Z, 40, 10, ],
        "left_shoulder_roll_joint": [ActuatorFIFSAType.FSA_TYPE_601780Z, 40, 10, ],
        "left_shoulder_yaw_joint": [ActuatorFIFSAType.FSA_TYPE_45_17_80Z, 25, 5, ],
        "left_elbow_pitch_joint": [ActuatorFIFSAType.FSA_TYPE_45_17_80Z, 25, 5, ],
        "left_wrist_yaw_joint": [ActuatorFIFSAType.FSA_TYPE_36_14_80Z, 10, 2.5, ],
        "left_wrist_pitch_joint": [ActuatorFIFSAType.FSA_TYPE_36_14_80Z, 10, 2.5, ],
        "left_wrist_roll_joint": [ActuatorFIFSAType.FSA_TYPE_36_14_80Z, 10, 2.5, ],
        # right arm
        "right_shoulder_pitch_joint": [ActuatorFIFSAType.FSA_TYPE_601780Z, 40, 10, ],
        "right_shoulder_roll_joint": [ActuatorFIFSAType.FSA_TYPE_601780Z, 40, 10, ],
        "right_shoulder_yaw_joint": [ActuatorFIFSAType.FSA_TYPE_45_17_80Z, 25, 5, ],
        "right_elbow_pitch_joint": [ActuatorFIFSAType.FSA_TYPE_45_17_80Z, 25, 5, ],
        "right_wrist_yaw_joint": [ActuatorFIFSAType.FSA_TYPE_36_14_80Z, 10, 2.5, ],
        "right_wrist_pitch_joint": [ActuatorFIFSAType.FSA_TYPE_36_14_80Z, 10, 2.5, ],
        "right_wrist_roll_joint": [ActuatorFIFSAType.FSA_TYPE_36_14_80Z, 10, 2.5, ],
    }

    return pd_dict


def GRMini1T1_pd_dict() -> dict:
    pd_dict = {
        "left_hip_pitch_joint": [ActuatorFIFSAType.FSA_TYPE_8029E, 180.0, 10.0],
        "left_hip_roll_joint": [ActuatorFIFSAType.FSA_TYPE_6043E, 120.0, 10.0],
        "left_hip_yaw_joint": [ActuatorFIFSAType.FSA_TYPE_6043E, 90.0, 8.0],
        "left_knee_pitch_joint": [ActuatorFIFSAType.FSA_TYPE_8029E, 120.0, 10.0],
        "left_ankle_roll_joint": [ActuatorFIFSAType.FSA_TYPE_4530E, 45.0, 2.5],
        "left_ankle_pitch_joint": [ActuatorFIFSAType.FSA_TYPE_4530E, 45.0, 2.5],

        "right_hip_pitch_joint": [ActuatorFIFSAType.FSA_TYPE_8029E, 180.0, 10.0],
        "right_hip_roll_joint": [ActuatorFIFSAType.FSA_TYPE_6043E, 120.0, 10.0],
        "right_hip_yaw_joint": [ActuatorFIFSAType.FSA_TYPE_6043E, 90.0, 8.0],
        "right_knee_pitch_joint": [ActuatorFIFSAType.FSA_TYPE_8029E, 120.0, 10.0],
        "right_ankle_roll_joint": [ActuatorFIFSAType.FSA_TYPE_4530E, 45.0, 2.5],
        "right_ankle_pitch_joint": [ActuatorFIFSAType.FSA_TYPE_4530E, 45.0, 2.5],

        "waist_yaw_joint": [ActuatorFIFSAType.FSA_TYPE_6043E, 90.0, 8.0],

        "left_shoulder_pitch_joint": [ActuatorFIFSAType.FSA_TYPE_6043E, 90.0, 8.0],
        "left_shoulder_roll_joint": [ActuatorFIFSAType.FSA_TYPE_4530E, 45.0, 2.5],
        "left_shoulder_yaw_joint": [ActuatorFIFSAType.FSA_TYPE_4530E, 45.0, 2.5],
        "left_elbow_pitch_joint": [ActuatorFIFSAType.FSA_TYPE_4530E, 45.0, 2.5],
        "left_wrist_yaw_joint": [ActuatorFIFSAType.FSA_TYPE_4530E, 45.0, 2.5],

        "right_shoulder_pitch_joint": [ActuatorFIFSAType.FSA_TYPE_6043E, 90.0, 8.0],
        "right_shoulder_roll_joint": [ActuatorFIFSAType.FSA_TYPE_4530E, 45.0, 2.5],
        "right_shoulder_yaw_joint": [ActuatorFIFSAType.FSA_TYPE_4530E, 45.0, 2.5],
        "right_elbow_pitch_joint": [ActuatorFIFSAType.FSA_TYPE_4530E, 45.0, 2.5],
        "right_wrist_yaw_joint": [ActuatorFIFSAType.FSA_TYPE_4530E, 45.0, 2.5],
    }

    return pd_dict


def GRMini1T2_pd_dict() -> dict:
    pd_dict = {
        "left_hip_pitch_joint": [ActuatorFIFSAType.FSA_TYPE_8029E, 180.0, 10.0],
        "left_hip_roll_joint": [ActuatorFIFSAType.FSA_TYPE_6043E, 120.0, 10.0],
        "left_hip_yaw_joint": [ActuatorFIFSAType.FSA_TYPE_6043E, 90.0, 8.0],
        "left_knee_pitch_joint": [ActuatorFIFSAType.FSA_TYPE_8029E, 120.0, 10.0],
        "left_ankle_roll_joint": [ActuatorFIFSAType.FSA_TYPE_4530E, 45.0, 2.5],
        "left_ankle_pitch_joint": [ActuatorFIFSAType.FSA_TYPE_4530E, 45.0, 2.5],

        "right_hip_pitch_joint": [ActuatorFIFSAType.FSA_TYPE_8029E, 180.0, 10.0],
        "right_hip_roll_joint": [ActuatorFIFSAType.FSA_TYPE_6043E, 120.0, 10.0],
        "right_hip_yaw_joint": [ActuatorFIFSAType.FSA_TYPE_6043E, 90.0, 8.0],
        "right_knee_pitch_joint": [ActuatorFIFSAType.FSA_TYPE_8029E, 120.0, 10.0],
        "right_ankle_roll_joint": [ActuatorFIFSAType.FSA_TYPE_4530E, 45.0, 2.5],
        "right_ankle_pitch_joint": [ActuatorFIFSAType.FSA_TYPE_4530E, 45.0, 2.5],

        "waist_yaw_joint": [ActuatorFIFSAType.FSA_TYPE_6043E, 90.0, 8.0],

        "left_shoulder_pitch_joint": [ActuatorFIFSAType.FSA_TYPE_6043E, 90.0, 8.0],
        "left_shoulder_roll_joint": [ActuatorFIFSAType.FSA_TYPE_4530E, 45.0, 2.5],
        "left_shoulder_yaw_joint": [ActuatorFIFSAType.FSA_TYPE_4530E, 45.0, 2.5],
        "left_elbow_pitch_joint": [ActuatorFIFSAType.FSA_TYPE_4530E, 45.0, 2.5],
        "left_wrist_yaw_joint": [ActuatorFIFSAType.FSA_TYPE_4530E, 45.0, 2.5],

        "right_shoulder_pitch_joint": [ActuatorFIFSAType.FSA_TYPE_6043E, 90.0, 8.0],
        "right_shoulder_roll_joint": [ActuatorFIFSAType.FSA_TYPE_4530E, 45.0, 2.5],
        "right_shoulder_yaw_joint": [ActuatorFIFSAType.FSA_TYPE_4530E, 45.0, 2.5],
        "right_elbow_pitch_joint": [ActuatorFIFSAType.FSA_TYPE_4530E, 45.0, 2.5],
        "right_wrist_yaw_joint": [ActuatorFIFSAType.FSA_TYPE_4530E, 45.0, 2.5],
    }

    return pd_dict


def GRTiny1Foot_pd_dict() -> dict:
    pd_dict = {
        "left_hip_roll_joint": [ActuatorFIFSAType.FSA_TYPE_8029E, 90.0, 7.0],
        "left_hip_pitch_joint": [ActuatorFIFSAType.FSA_TYPE_8029E, 90.0, 7.0],
        "left_knee_pitch_joint": [ActuatorFIFSAType.FSA_TYPE_8029E, 90.0, 7.0],
        "left_ankle_pitch_joint": [ActuatorFIFSAType.FSA_TYPE_4530E, 45.0, 2.5],

        "right_hip_roll_joint": [ActuatorFIFSAType.FSA_TYPE_8029E, 90.0, 7.0],
        "right_hip_pitch_joint": [ActuatorFIFSAType.FSA_TYPE_8029E, 90.0, 7.0],
        "right_knee_pitch_joint": [ActuatorFIFSAType.FSA_TYPE_8029E, 90.0, 7.0],
        "right_ankle_pitch_joint": [ActuatorFIFSAType.FSA_TYPE_4530E, 45.0, 2.5],
    }

    return pd_dict


def GRTiny1Wheel_pd_dict() -> dict:
    pd_dict = {
        "left_hip_roll_joint": [ActuatorFIFSAType.FSA_TYPE_8029E, 90.0, 7.0],
        "left_hip_pitch_joint": [ActuatorFIFSAType.FSA_TYPE_8029E, 90.0, 7.0],
        "left_knee_pitch_joint": [ActuatorFIFSAType.FSA_TYPE_8029E, 90.0, 7.0],
        "left_ankle_wheel_joint": [ActuatorFIFSAType.FSA_TYPE_8010E, 0.0, 1.0],

        "right_hip_roll_joint": [ActuatorFIFSAType.FSA_TYPE_8029E, 90.0, 7.0],
        "right_hip_pitch_joint": [ActuatorFIFSAType.FSA_TYPE_8029E, 90.0, 7.0],
        "right_knee_pitch_joint": [ActuatorFIFSAType.FSA_TYPE_8029E, 90.0, 7.0],
        "right_ankle_wheel_joint": [ActuatorFIFSAType.FSA_TYPE_8010E, 0.0, 1.0],
    }

    return pd_dict


def print_pd_converted():
    Logger().print_info("start")

    pid_dict_converted = pd_conversion.pd_conversion_dict(GR2T3_dic_pd_dict())

    for key, value in pid_dict_converted.items():
        Logger().print_info(f"{key}, {value}")

    Logger().print_info("end")


if __name__ == "__main__":
    print_pd_converted()
