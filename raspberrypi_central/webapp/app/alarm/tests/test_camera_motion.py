import uuid
from unittest.mock import Mock

from django.db.models.fields.files import ImageFieldFile
from django.test import TestCase

from alarm.business.camera_motion import CameraMotion
from alarm.communication.in_motion import save_motion
from camera.models import CameraMotionDetected, CameraMotionDetectedPicture
from devices.factories import DeviceFactory


class CameraMotionTestCase(TestCase):
    def setUp(self) -> None:
        self.device = DeviceFactory()
        self.event_ref = uuid.uuid4()

        self.create_and_send_notification = Mock()
        self.play_sound = Mock()
        self.send_picture = Mock()

    def test_camera_motion_detected(self):
        camera_motion = CameraMotion(save_motion, self.create_and_send_notification, self.send_picture, self.play_sound)

        camera_motion.camera_motion_detected(self.device.device_id, {}, str(self.event_ref), True)
        self.play_sound.assert_called_once_with(self.device.device_id, True)
        self.create_and_send_notification.apply_async.assert_called_once()

        motion = CameraMotionDetected.objects.filter(event_ref=str(self.event_ref), device=self.device)
        self.assertTrue(len(motion), 1)

    def test_camera_motion_no_more_motion(self):
        camera_motion = CameraMotion(save_motion, self.create_and_send_notification, self.send_picture, self.play_sound)

        camera_motion.camera_motion_detected(self.device.device_id, {}, str(self.event_ref), True)
        self.create_and_send_notification.reset_mock()
        self.play_sound.reset_mock()

        camera_motion.camera_motion_detected(self.device.device_id, {}, str(self.event_ref), False)
        self.play_sound.assert_called_once_with(self.device.device_id, False)
        self.create_and_send_notification.apply_async.assert_called_once()

        motion = CameraMotionDetected.objects.filter(event_ref=str(self.event_ref), device=self.device)
        self.assertTrue(len(motion), 1)

    def test_camera_motion_picture(self):
        fake_picture_path = '/some/path.png'

        camera_motion = CameraMotion(save_motion, self.create_and_send_notification, self.send_picture, self.play_sound)
        camera_motion.camera_motion_picture(self.device.device_id, fake_picture_path, str(self.event_ref), True)

        motion = CameraMotionDetectedPicture.objects.filter(event_ref=str(self.event_ref), device=self.device)
        self.assertTrue(len(motion), 1)
        motion = motion[0]

        self.assertEqual(motion.motion_started_picture.name, 'path.png')
        self.assertEqual(motion.motion_ended_picture.name, '')

        kwargs = {
            'picture_path': fake_picture_path
        }

        self.send_picture.assert_called_once_with(kwargs=kwargs)

    def test_camera_motion_picture_no_more_motion(self):
        fake_picture_path = '/some/path.png'
        fake_picture_path2 = '/some/path2.png'

        camera_motion = CameraMotion(save_motion, self.create_and_send_notification, self.send_picture, self.play_sound)
        camera_motion.camera_motion_picture(self.device.device_id, fake_picture_path, str(self.event_ref), True)
        camera_motion.camera_motion_picture(self.device.device_id, fake_picture_path2, str(self.event_ref), False)

        motion = CameraMotionDetectedPicture.objects.filter(event_ref=str(self.event_ref), device=self.device)
        self.assertTrue(len(motion), 1)
        motion = motion[0]

        self.assertEqual(motion.motion_started_picture.name, 'path.png')
        self.assertEqual(motion.motion_ended_picture.name, 'path2.png')
