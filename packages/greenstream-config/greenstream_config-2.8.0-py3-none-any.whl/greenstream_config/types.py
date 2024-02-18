from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Offsets:
    # in radians in FLU
    roll: Optional[float] = None
    pitch: Optional[float] = None
    yaw: Optional[float] = None
    forward: Optional[float] = None
    left: Optional[float] = None
    up: Optional[float] = None


@dataclass
class Camera:
    # This will become the name of frame-id, ros topic and webrtc stream
    name: str
    # Used to order the stream in the UI
    order: int
    # An array of gstream source / transform elements e.g.
    # ["v4l2src", "video/x-raw, format=RGB,width=1920,height=1080"]
    elements: List[str]
    pixel_width: int
    pixel_height: int
    sensor_width_mm: float
    sensor_height_mm: float
    focal_length_mm: float
    fov: float
    camera_frame_topic: str
    camera_info_topic: str
    camera_info_ext_topic: str
    # The camera's position relative to the vessel base_link
    offsets: Optional[Offsets] = None
    type: str = "color"


@dataclass
class CameraOverride:
    # This will become the name of frame-id, ros topic and webrtc stream
    name: Optional[str]
    order: Optional[int]
    # An array of gstream source / transform elements e.g.
    # ["v4l2src", "video/x-raw, format=RGB,width=1920,height=1080"]
    elements: Optional[List[str]]
    pixel_width: Optional[int]
    pixel_height: Optional[int]
    sensor_width_mm: Optional[float]
    sensor_height_mm: Optional[float]
    focal_length_mm: Optional[float]
    fov: Optional[float]
    camera_frame_topic: Optional[str]
    camera_info_topic: Optional[str]
    camera_info_ext_topic: Optional[str]
    type: Optional[str] = "color"
    # The camera's position relative to the vessel base_link
    offsets: Optional[Offsets] = None


@dataclass
class GreenstreamConfig:
    cameras: List[Camera]
    camera_overrides: Optional[List[Optional[CameraOverride]]] = None
    signalling_server_port: int = 8443
    namespace: str = ""  # eg. vessel_1
    ui_port: int = 8080
    mode: str = "simulator"
    variant: str = ""   
    ros_throttle_time: float = 0.0000001
