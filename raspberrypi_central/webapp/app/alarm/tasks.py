from __future__ import absolute_import, unicode_literals
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from celery import shared_task
import paho.mqtt.client as mqtt
import os

from alarm import models as alarm_models
from house import models as house_models
from devices import models as device_models
from notification.tasks import send_message

def create_mqtt_client(mqtt_user: str, mqtt_pswd: str, mqtt_hostname: str, mqtt_port: str):
    client = mqtt.Client(client_id='rpi4-mqtt-listen-django', clean_session=False)
    client.username_pw_set(mqtt_user, mqtt_pswd)

    client.connect(mqtt_hostname, int(mqtt_port), keepalive=120)

    return client

def create_mqtt_client(mqtt_user: str, mqtt_pswd: str, mqtt_hostname: str, mqtt_port: str, client_name = None):

    if client_name is None:
        clean_session = True
    else:
        False

    client = mqtt.Client(client_id=client_name, clean_session=client_name)
    client.username_pw_set(mqtt_user, mqtt_pswd)

    client.connect(mqtt_hostname, int(mqtt_port), keepalive=120)

    return client


class AlarmMessaging():

    def __init__(self, mqtt_user: str, mqtt_pswd: str, mqtt_hostname: str, mqtt_port: str, mqtt_alarm_camera_topic):
        self.mqtt_user = mqtt_user
        self.mqtt_pswd = mqtt_pswd
        self.mqtt_hostname = mqtt_hostname
        self.mqtt_port = mqtt_port
        self.mqtt_alarm_camera_topic = mqtt_alarm_camera_topic

        self.client = self._mqtt_connect()

    def _mqtt_connect(self):
        client = mqtt.Client()
        client.username_pw_set(self.mqtt_user, self.mqtt_pswd)

        client.connect(self.mqtt_hostname, int(self.mqtt_port), keepalive=120)

        return client
    
    def set_status(self, status: bool):
        self.client.publish(self.mqtt_alarm_camera_topic, status, qos=1)


@shared_task(name="security.camera_motion_picture", bind=True)
def camera_motion_picture(self, picture_path):
    picture = alarm_models.CameraMotionDetectedPicture(picture_path=picture_path)
    picture.save()

    kwargs = {
        'picture_path': picture_path
    }
    send_message.apply_async(kwargs=kwargs)


@shared_task(name="security.play_sound")
def play_sound(motion_came_from_device_id: str):
    # device = device_models.Device.objects.get(device_id=device_id)
    mqtt_client = create_mqtt_client(
        os.environ['MQTT_USER'],
        os.environ['MQTT_PASSWORD'],
        os.environ['MQTT_HOSTNAME'],
        os.environ['MQTT_PORT']
    )

    mqtt_client.publish('status/sound', str(True), qos=1)


@shared_task(name="security.camera_motion_detected")
def camera_motion_detected(device_id: str):
    device = device_models.Device.objects.get(device_id=device_id)
    alarm_models.CameraMotionDetected.objects.create(device=device)

    location = device.location

    kwargs = {
        'message': f'Une présence étrangère a été détectée chez vous depuis {device_id} {location.structure} {location.sub_structure}'
    }

    send_message.apply_async(kwargs=kwargs)
    play_sound.apply_async(kwargs={'motion_came_from_device_id': device_id})


@shared_task(name="alarm.set_alarm_off")
def set_alarm_off():
    s = alarm_models.AlarmStatus(running=False)
    s.save()


@shared_task(name="alarm.set_alarm_on")
def set_alarm_on():
    s = alarm_models.AlarmStatus(running=True)
    s.save()


@shared_task
def alarm_status_changed(status: bool):
    alarm_messaging = AlarmMessaging(
        os.environ['MQTT_USER'],
        os.environ['MQTT_PASSWORD'],
        os.environ['MQTT_HOSTNAME'],
        os.environ['MQTT_PORT'],
        'motion/camera')

    alarm_messaging.set_status(status)

    kwargs = {
        'message': f'Votre alarme a changée de status: {status}'
    }
    send_message.apply_async(kwargs=kwargs)
