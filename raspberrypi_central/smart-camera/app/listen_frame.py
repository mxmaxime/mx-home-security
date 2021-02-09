import io
import os
from typing import Dict

from camera.camera import Camera
from camera.camera_factory import camera_factory
from camera.dumb_camera import DumbCamera
from camera_analyze.camera_analyzer import CameraAnalyzer
from mqtt.mqtt_client import get_mqtt
from camera.camera_record import DumbCameraRecord
from mqtt.mqtt_status_manage_thread import mqtt_status_manage_thread_factory
from service_manager.roi_camera_from_args import roi_camera_from_args
from service_manager.runnable import Runnable


def extract_data_from_topic(topic: str):
    split = topic.split('/')

    return {
        'device_id': split[2]
    }


DEVICE_ID = os.environ['DEVICE_ID']

mqtt_client = get_mqtt(f'{DEVICE_ID}-analyzer')
mqtt_client.connect()


class ConnectedDevices:
    """
    Wrapper around the datastructures to hold connected devices with their configuration.
    So if we need multiprocessing in the future, we can do it here.
    """

    def __init__(self):
        self._connected_devices: Dict[str, Camera] = {}

    def remove(self, device_id: str) -> None:
        self._connected_devices.pop(device_id, None)

    def has(self, device_id: str) -> bool:
        return device_id in self._connected_devices

    def update(self, device_id: str, camera_analyzer: CameraAnalyzer) -> None:
        if not self.has(device_id):
            return None

        camera = self._connected_devices[device_id]

        if camera.analyze_motion != camera_analyzer:
            self._connected_devices[device_id].analyze_motion = camera_analyzer

    def add(self, device_id: str, camera_analyzer: CameraAnalyzer) -> None:
        camera = camera_factory(get_mqtt, camera_analyzer)
        camera.start()

        camera_record = DumbCameraRecord(mqtt_client.client)
        camera.camera_recorder = camera_record

        self._connected_devices[device_id] = camera

    @property
    def connected_devices(self) -> Dict[str, Camera]:
        return self._connected_devices


class FrameReceiver:
    def __init__(self, connected_devices: ConnectedDevices):
        self._connected_devices = connected_devices

    def on_picture(self, client, userdata, message):
        data = extract_data_from_topic(message.topic)
        from_device_id = data['device_id']

        image = io.BytesIO(message.payload)

        camera = self._connected_devices.connected_devices.get(from_device_id, None)
        print(f'on picture analyze {from_device_id} {camera}')

        if camera:
            camera.process_frame(image, from_device_id)

class CameraManager(Runnable):

    def __init__(self, connected_devices: ConnectedDevices):
        self._connected_devices = connected_devices

    def run(self, device_id: str, status: bool, data=None) -> None:
        if status is False:
            self._connected_devices.remove(device_id)
            return None

        camera_analyze_object = roi_camera_from_args(data)

        if self._connected_devices.has(device_id):
            pass
            # todo: check if analyzer differ to remove/add new config
            # try to keep the same Camera object to avoid mqtt disconnect/reconnect.
            # could be able to do it because its a composition
        else:
            self._connected_devices.add(device_id, camera_analyze_object)


connected_devices = ConnectedDevices()

frame_receiver = FrameReceiver(connected_devices)

# topics to receive frames to analyze for dumb cameras.
mqtt_client.client.subscribe(f'{DumbCamera.PICTURE_TOPIC}/+', qos=1)
mqtt_client.client.message_callback_add(f'{DumbCamera.PICTURE_TOPIC}/+', frame_receiver.on_picture)

# topics to know when a camera is up/off
camera_manager = CameraManager(connected_devices)
mqtt_status_manage_thread_factory(None, 'camera', get_mqtt(f"{DEVICE_ID}-listen-dumb-camera-manager"), camera_manager, status_json=True)

mqtt_client.client.loop_forever()