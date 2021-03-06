from typing import Dict

from camera.camera_object_detection import CameraObjectDetection
from camera.camera_object_detection_factory import camera_object_detection_factory
from camera.camera_record import DumbCameraRecorder
from object_detection.detect_people_factory import detect_people_factory
from service_manager.runnable import Runnable

DETECT_PEOPLE = detect_people_factory()

def dumb_camera_factory(mqtt, device_id: str) -> CameraObjectDetection:
    camera_record = DumbCameraRecorder(mqtt.client, device_id)
    camera = camera_object_detection_factory(device_id, camera_record, DETECT_PEOPLE)
    camera.start()

    return camera

class ConnectedDevices:
    """
    Wrapper around the datastructures to hold connected devices with their configuration.
    So if we need multiprocessing in the future, we can do it here.
    """

    def __init__(self, mqtt):
        self._mqtt = mqtt
        self._connected_devices: Dict[str, CameraObjectDetection] = {}

    def remove(self, device_id: str) -> None:
        if device_id in self._connected_devices:
            object_detection = self._connected_devices.pop(device_id, None)
            if object_detection:
                object_detection.stop()

    def has(self, device_id: str) -> bool:
        return device_id in self._connected_devices

    def add(self, device_id: str) -> None:
        camera = dumb_camera_factory(self._mqtt, device_id)
        self._connected_devices[device_id] = camera

    @property
    def connected_devices(self) -> Dict[str, CameraObjectDetection]:
        return self._connected_devices


class RunListenFrame(Runnable):

    def __init__(self, connected_devices: ConnectedDevices):
        self._connected_devices = connected_devices

    def run(self, device_id: str, status: bool, data=None) -> None:
        if status is False:
            self._connected_devices.remove(device_id)
            return None


        if self._connected_devices.has(device_id):
            pass
            # todo: check if analyzer differ to remove/add new config
            # try to keep the same Camera object to avoid mqtt disconnect/reconnect.
            # could be able to do it because its a composition
        else:
            self._connected_devices.add(device_id)
