from unittest.mock import Mock, patch
from django.test import TestCase
from alarm.mqtt.on_connected_services import OnConnectedCameraManager, OnConnectedObjectDetection, OnConnectedCamera
from alarm.factories import AlarmStatusFactory
from devices.factories import DeviceFactory


class OnConnectedObjectDetectionTestCase(TestCase):
    def setUp(self) -> None:
        self.device = DeviceFactory()
        self.alarm_status = AlarmStatusFactory(device=self.device)
        self.mqtt = Mock()

    def test_on_connect_close_motions(self):
        handler = OnConnectedObjectDetection(self.mqtt)

        with patch('camera.business.camera_motion.close_unclosed_camera_motions') as camera_motion:
            handler.on_connect('serivce_name', self.device.device_id)

            camera_motion.assert_called_once_with(self.device.device_id)

    def test_on_disconnect_close_motion(self):
        handler = OnConnectedObjectDetection(self.mqtt)

        with patch('camera.business.camera_motion.close_unclosed_camera_motions') as camera_motion:
            handler.on_disconnect('serivce_name', self.device.device_id)

            camera_motion.assert_called_once_with(self.device.device_id)


class OnConnectedCameraManagerTestCase(TestCase):
    def setUp(self) -> None:
        self.device = DeviceFactory()
        self.alarm_status = AlarmStatusFactory(device=self.device)
        self.mqtt = Mock()


    def test_on_connect_send_data(self):
        handler = OnConnectedCameraManager(self.mqtt)

        with patch('alarm.use_cases.out_alarm.notify_alarm_status_factory') as notify_alarm_status_factory:
            notify = Mock()
            notify_alarm_status_factory.return_value = notify

            handler.on_connect('serivce_name', self.device.device_id)
            notify.publish_device_connected.assert_called_once_with(self.device.device_id)

