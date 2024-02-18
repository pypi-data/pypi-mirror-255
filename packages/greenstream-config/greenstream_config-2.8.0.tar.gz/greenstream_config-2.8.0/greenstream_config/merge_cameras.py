from typing import List, Optional

from greenstream_config.types import Camera, CameraOverride


def merge_cameras(
    cameras: List[Camera], overrides: List[Optional[CameraOverride]]
) -> List[Camera]:
    """
    The gama_vessel may contain camera overrides.
    If it does, we need to merge them with the default cameras.
    """

    if overrides is None:
        return cameras

    overriden_cameras: List[Camera] = cameras
    for idx, override in enumerate(overrides):
        # If override is null/None, we don't want to override the default camera
        if override:
            if idx < len(overriden_cameras):

                # applies changes to the camera only if attribute is not None
                overriden_cameras[idx] = Camera(
                    name=override.name or cameras[idx].name,
                    order=override.order or cameras[idx].order,
                    elements=override.elements or cameras[idx].elements,
                    offsets=override.offsets or cameras[idx].offsets,
                    pixel_width=override.pixel_width or cameras[idx].pixel_width,
                    pixel_height=override.pixel_height or cameras[idx].pixel_height,
                    sensor_width_mm=override.sensor_width_mm or cameras[idx].sensor_width_mm,
                    sensor_height_mm=override.sensor_height_mm or cameras[idx].sensor_height_mm,
                    focal_length_mm=override.focal_length_mm or cameras[idx].focal_length_mm,
                    fov=override.fov or cameras[idx].fov,
                    camera_frame_topic=override.camera_frame_topic
                    or cameras[idx].camera_frame_topic,
                    camera_info_topic=override.camera_info_topic or cameras[idx].camera_info_topic,
                    camera_info_ext_topic=override.camera_info_ext_topic
                    or cameras[idx].camera_info_ext_topic,
                    type=override.type or cameras[idx].type,
                )
            # else:
            #     overriden_cameras.append(
            #         Camera(
            #             name=override.name,
            #             order=override.order,
            #             elements=override.elements,
            #             offsets=override.offsets,
            #             pixel_width=override.pixel_width,
            #             pixel_height=override.pixel_height,
            #             sensor_width_mm=override.sensor_width_mm,
            #             sensor_height_mm=override.sensor_height_mm,
            #             focal_length_mm=override.focal_length_mm,
            #             fov=override.fov,
            #             camera_frame_topic=override.camera_frame_topic,
            #             camera_info_topic=override.camera_info_topic,
            #             camera_info_ext_topic=override.camera_info_ext_topic,
            #             type=override.type,
            #         )
            #     )

    return overriden_cameras
