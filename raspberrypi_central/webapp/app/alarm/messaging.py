import struct


class MqttStatus():
    def __init__(self, mqtt_client):
        self._mqtt_client = mqtt_client

    def publish(self, topic, message: bool):
        status_bytes = struct.pack('?', message)
        print(f'send status: {status_bytes} on {topic}')
        self._mqtt_client.publish(topic, status_bytes, qos=1, retain=True)


class SpeakerMessaging():
    def __init__(self, mqtt_status: MqttStatus):
        self._mqtt_status = mqtt_status

    def publish_speaker_status(self, device_id: str, status: bool):
        self._mqtt_status.publish(f'status/speaker/{device_id}', status)


class AlarmMessaging():

    def __init__(self, mqtt_status: MqttStatus, speaker_messaging: SpeakerMessaging):
        self._mqtt_status = mqtt_status
        self._speaker_messaging = speaker_messaging

    def publish_alarm_status(self, device_id: str, status: bool):
        self._mqtt_status.publish(f'status/camera/{device_id}', status)

        if status is False:
            self._speaker_messaging.publish_speaker_status(device_id, False)


def speaker_messaging_factory(mqtt_client):
    mqtt_status = MqttStatus(mqtt_client)

    return SpeakerMessaging(mqtt_status)


def alarm_messaging_factory(mqtt_client):
    mqtt_status = MqttStatus(mqtt_client)
    speaker = speaker_messaging_factory(mqtt_client)

    return AlarmMessaging(mqtt_status, speaker)