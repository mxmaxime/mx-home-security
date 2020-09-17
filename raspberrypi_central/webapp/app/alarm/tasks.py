from celery import shared_task
from alarm import models as alarm_models
from devices import models as device_models
from notification.tasks import send_message
from standalone.mqtt import mqtt_factory
from .messaging import alarm_messaging_factory


@shared_task(name="security.camera_motion_picture", bind=True)
def camera_motion_picture(self, device_id: str, picture_path: str):
    # TODO #91 link camera motion to device_id
    picture = alarm_models.CameraMotionDetectedPicture(picture_path=picture_path)
    picture.save()

    kwargs = {
        'picture_path': picture_path
    }

    send_message.apply_async(kwargs=kwargs)


@shared_task(name="security.play_sound")
def play_sound(motion_came_from_device_id: str):
    # device = device_models.Device.objects.get(device_id=device_id)
    mqtt_client = mqtt_factory()

    alarm_messaging = alarm_messaging_factory(mqtt_client)
    alarm_messaging.publish_sound_status(True)


@shared_task(name="security.camera_motion_detected")
def camera_motion_detected(device_id: str):
    device = device_models.Device.objects.get(device_id=device_id)
    alarm_models.CameraMotionDetected.objects.create(device=device)

    location = device.location

    kwargs = {
        'message': f'Une présence étrangère a été détectée chez vous depuis {device_id} {location.structure} {location.sub_structure}'
    }

    # TODO: check if this is a correct way to create & run multiple jobs.
    # ! They are not related, they have to run in total parallel.
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
def alarm_status_changed(device_id: str, status: bool):
    mqtt_client = mqtt_factory()

    alarm_messaging = alarm_messaging_factory(mqtt_client)
    alarm_messaging.publish_alarm_status(device_id, status)

    kwargs = {
        'message': f'Votre alarme {device_id} a changée de status: {status}'
    }

    send_message.apply_async(kwargs=kwargs)
