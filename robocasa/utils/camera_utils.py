"""
Collection of constants for cameras / robots / etc
in kitchen environments
"""

# default free cameras for different kitchen layouts
LAYOUT_CAMS = {
    0: dict(
        lookat=[2.26593463, -1.00037131, 1.38769295],
        distance=3.0505089839567323,
        azimuth=90.71563812375285,
        elevation=-12.63948837207208,
    ),
    1: dict(
        lookat=[2.66147999, -1.00162429, 1.2425155],
        distance=3.7958766287746255,
        azimuth=89.75784013699234,
        elevation=-15.177406642875091,
    ),
    2: dict(
        lookat=[3.02344359, -1.48874618, 1.2412914],
        distance=3.6684844368165512,
        azimuth=51.67880851867874,
        elevation=-13.302619131542388,
    ),
    # 3: dict(
    #     lookat=[11.44842548, -11.47664723, 11.24115989],
    #     distance=43.923271794728187,
    #     azimuth=227.12928449329333,
    #     elevation=-16.495686334624907,
    # ),
    4: dict(
        lookat=[1.6, -1.0, 1.0],
        distance=5,
        azimuth=89.70301806083651,
        elevation=-18.02177994296577,
    ),
}

DEFAULT_LAYOUT_CAM = {
    "lookat": [2.25, -1, 1.05312667],
    "distance": 5,
    "azimuth": 89.70301806083651,
    "elevation": -18.02177994296577,
}

import numpy as np
from scipy.spatial.transform import Rotation


def get_camera_direction_quat(look_at, up=[0, 0, 1]):
    """
    카메라가 특정 방향을 바라보도록 하는 쿼터니온을 계산합니다.
    look_at: 카메라가 바라볼 방향 벡터
    up: 카메라의 상단 방향 벡터
    """
    look_at = np.array(look_at) / np.linalg.norm(look_at)
    up = np.array(up) / np.linalg.norm(up)
    right = np.cross(look_at, up)
    up = np.cross(right, look_at)
    rot_matrix = np.array([right, up, -look_at]).T
    return Rotation.from_matrix(rot_matrix).as_quat()


# 주방을 바라보는 방향 (x축 음의 방향)
main_wall_direction = [-1, 0, 0]
camera_quat = get_camera_direction_quat(main_wall_direction)

# y축을 중심으로 90도 회전을 추가
y_rotation = Rotation.from_euler("y", 90, degrees=True)
camera_quat_rotated = (y_rotation * Rotation.from_quat(camera_quat)).as_quat()

CAM_CONFIGS = dict(
    robot0_agentview_center=dict(
        pos=[2.0, 0.0, 1.4],  # 주방 오른쪽에서 바라보는 위치
        quat=camera_quat_rotated,
    ),
    robot0_agentview_left=dict(
        pos=[2.0, -0.5, 1.4],
        quat=camera_quat_rotated,
        camera_attribs=dict(fovy="60"),
    ),
    robot0_agentview_right=dict(
        pos=[2.0, 0.5, 1.4],
        quat=camera_quat_rotated,
        camera_attribs=dict(fovy="60"),
    ),
    robot0_frontview=dict(
        pos=[-0.50, 0, 0.95],
        quat=[
            0.6088936924934387,
            0.3814677894115448,
            -0.3673907518386841,
            -0.5905545353889465,
        ],
        camera_attribs=dict(fovy="60"),
        parent_body="base0_support",
    ),
    robot0_eye_in_hand=dict(
        pos=[0.05, 0, 0],
        quat=[0, 0.707107, 0.707107, 0],
        parent_body="robot0_right_hand",
    ),
    # new_camera=dict(
    #     pos=[0.0, 0.0, 0.0],
    #     quat=[0.0, 0.0, 0.0, 1.0],
    #     parent_body="",
    # ),
)
