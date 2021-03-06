from alarm.mqtt import MqttServices
from camera.messaging import CameraMessaging, camera_messaging_factory
from utils.mqtt.mqtt_status import MqttBooleanStatus, MqttJsonStatus

from camera.messaging import CameraData


class SpeakerMessaging:
    def __init__(self, mqtt_status: MqttBooleanStatus):
        self._mqtt_status = mqtt_status

    def publish_speaker_status(self, device_id: str, status: bool):
        self._mqtt_status.publish(f'status/{MqttServices.SPEAKER.value}/{device_id}', status)


class AlarmMessaging:
    """Class to communicate with Alarm services (through mqtt).

    """
    def __init__(self, mqtt_status: MqttJsonStatus, speaker_messaging: SpeakerMessaging, camera_messaging: CameraMessaging):
        self._mqtt_status = mqtt_status
        self._speaker_messaging = speaker_messaging
        self._camera_messaging = camera_messaging

    def publish_alarm_status(self, device_id: str, status: bool, is_dumb: bool, data=None) -> None:
        self._mqtt_status.publish(f'status/{MqttServices.OBJECT_DETECTION_MANAGER.value}/{device_id}', status, data)

        camera_cara = CameraData(to_analyze=True) if status else CameraData(to_analyze=False)
        self._camera_messaging.publish_status(device_id, status, camera_cara)

        if status is False:
            self._speaker_messaging.publish_speaker_status(device_id, False)


def speaker_messaging_factory(mqtt_client):
    mqtt_status = MqttBooleanStatus(mqtt_client)

    return SpeakerMessaging(mqtt_status)


def alarm_messaging_factory(mqtt_client):
    mqtt_status = MqttJsonStatus(mqtt_client)
    speaker = speaker_messaging_factory(mqtt_client)
    camera = camera_messaging_factory(mqtt_client)

    return AlarmMessaging(mqtt_status, speaker, camera)
