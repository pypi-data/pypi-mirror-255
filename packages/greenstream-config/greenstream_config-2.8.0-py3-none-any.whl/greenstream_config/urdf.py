from typing import List, Optional, Tuple

from urchin import Joint, Link, xyz_rpy_to_matrix

from greenstream_config.merge_cameras import merge_cameras
from greenstream_config.types import Camera, CameraOverride


def get_camera_urdf(
    camera: Camera, add_optical_frame: bool = True
) -> Tuple[List[Link], List[Joint]]:
    # This is the camera urdf from the gama/lookout greenstream.launch.py
    # We need to generate this from the camera config
    camera_xyz_rpy = [camera.offsets.forward or 0.0,
                    camera.offsets.left or 0.0,
                    camera.offsets.up or 0.0,
                    camera.offsets.roll or 0.0,
                    camera.offsets.pitch or 0.0,
                    camera.offsets.yaw or 0.0,
                    ] if camera.offsets else [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

    links = [Link(name=f"{camera.name}_link", inertial=None, visuals=None, collisions=None)]
    joints = [
        Joint(
            name=f"{camera.name}_joint",
            parent="base_link",
            child=f"{camera.name}_link",
            joint_type="fixed",
            origin=xyz_rpy_to_matrix(camera_xyz_rpy),
        )
    ]

    if add_optical_frame:
        links.append(
            Link(
                name=f"{camera.name}_{camera.type}_frame",
                inertial=None,
                visuals=None,
                collisions=None,
            )
        )
        links.append(
            Link(
                name=f"{camera.name}_{camera.type}_optical_frame",
                inertial=None,
                visuals=None,
                collisions=None,
            )
        )

        # fixed transforms between camera frame and optical frame FRD -> NED
        joints.append(
            Joint(
                name=f"{camera.name}_link_to_{camera.type}_frame",
                parent=f"{camera.name}_link",
                child=f"{camera.name}_{camera.type}_frame",
                joint_type="fixed",
                origin=xyz_rpy_to_matrix([0, 0, 0, 0, 0, 0]),
            )
        )
        joints.append(
            Joint(
                name=f"{camera.name}_{camera.type}_frame_to_optical_frame",
                parent=f"{camera.name}_{camera.type}_frame",
                child=f"{camera.name}_{camera.type}_optical_frame",
                joint_type="fixed",
                origin=xyz_rpy_to_matrix([0, 0, 0, -1.570796, 0, -1.570796]),
            )
        )

    return (links, joints)


def get_cameras_urdf(
    cameras: List[Camera],
    camera_overrides: List[Optional[CameraOverride]],
    add_optical_frame: bool = True,
) -> Tuple[List[Link], List[Joint]]:

    links: List[Link] = []
    joints: List[Joint] = []
    cameras = merge_cameras(cameras, camera_overrides)

    # assume cameras have already been merged with overrides
    for camera in cameras:
        camera_links, camera_joints = get_camera_urdf(camera, add_optical_frame)
        links += camera_links
        joints += camera_joints

    return links, joints
