import json
import uuid
from django_celery_beat.models import CrontabSchedule, PeriodicTask
from django.db import models
from house.models import House
from utils.mqtt import mqtt_factory
from devices.models import Device
from alarm.communication.alarm import NotifyAlarmStatus

class AlarmStatusManager(models.Manager):
    def get_status(self):
        # TODO: we will remove this for issue #86
        return self.all().first()


class AlarmStatus(models.Model):
    objects = AlarmStatusManager()

    running = models.BooleanField()
    device = models.OneToOneField(Device, on_delete=models.PROTECT)

    def save(self, *args, **kwargs):
        NotifyAlarmStatus(mqtt_factory).publish(self.device.device_id, self.running)
        super().save(*args, **kwargs)

    def __str__(self):
        return f'Status is {self.running} for {self.device}'


class CameraROI(models.Model):
    device = models.OneToOneField(Device, on_delete=models.PROTECT)

    """
    We save the picture where the user defined the ROI.
    This could be useful to check if the camera moves to let know the user
    because the ROI could become wrong.
    """
    define_picture = models.ImageField()


class CameraRectangleROI(models.Model):
    # ? We might rework the max_digits & decimal_places here
    # I didn't really know what to put here. Seems good but may not be optimized.

    x = models.DecimalField(max_digits=8, decimal_places=4)
    y = models.DecimalField(max_digits=8, decimal_places=4)
    w = models.DecimalField(max_digits=8, decimal_places=4)
    h = models.DecimalField(max_digits=8, decimal_places=4)

    camera_roi = models.ForeignKey(CameraROI, on_delete=models.CASCADE)

    # TODO: use a service to change rectangle ROI.
    # def save(self, *args, **kwargs):
    #     NotifyAlarmStatus(mqtt_factory).publish(self.device.device_id)
    #     super().save(*args, **kwargs)


class AlarmSchedule(models.Model):
    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    hour_start = models.IntegerField()
    minute_start = models.IntegerField()

    hour_end = models.IntegerField()
    minute_end = models.IntegerField()

    monday    = models.BooleanField()
    tuesday   = models.BooleanField()
    wednesday = models.BooleanField()
    thursday  = models.BooleanField()
    friday    = models.BooleanField()
    saturday  = models.BooleanField()
    sunday    = models.BooleanField()

    is_disabled_by_system = models.BooleanField(default=False)

    turn_on_task = models.OneToOneField(PeriodicTask, blank=True, null=True, on_delete=models.CASCADE, related_name='alarm_schedule_on')
    turn_off_task = models.OneToOneField(PeriodicTask, blank=True, null=True, on_delete=models.CASCADE, related_name='alarm_schedule_off')

    alarm_statuses = models.ForeignKey(AlarmStatus, on_delete=models.PROTECT)

    def save(self, *args, **kwargs):
        days = []

        def model_boolean_fields_to_cron_days():
            possible_days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']

            """
            Celery "day_of_the_week" inputs: "A (list of) integers from 0-6, where Sunday = 0 and Saturday = 6, that represent the days of a week that execution should occur."
            https://docs.celeryproject.org/en/latest/reference/celery.schedules.html#celery.schedules.crontab.day_of_week
            So we are mapping values to int.
            """
            for day_int, day_str in enumerate(possible_days, start=0):
                if getattr(self, day_str):
                    days.append(str(day_int))
        
            # Celery crontab want a list as str, ex: "monday,tuesday,..."
            cron_days = ','.join(days)

            return cron_days

        cron_days = model_boolean_fields_to_cron_days()

        house_timezone = House.objects.get_system_house().timezone
        self.uuid = str(uuid.uuid4())

        if self._state.adding is True:
            schedule_turn_on_alarm = CrontabSchedule.objects.create(
                minute=self.minute_start,
                hour=self.hour_start,
                day_of_week=cron_days,
                timezone=house_timezone
            )

            self.turn_on_task = PeriodicTask.objects.create(
                name=f'Turn on alarm {self.uuid}',
                task='alarm.set_alarm_on',
                crontab=schedule_turn_on_alarm,
                args=json.dumps([self.uuid])
            )

            schedule_turn_off_alarm = CrontabSchedule.objects.create(
                minute=self.minute_end,
                hour=self.hour_end,
                day_of_week=cron_days,
                timezone=house_timezone
            )

            self.turn_off_task = PeriodicTask.objects.create(
                name=f'Turn off alarm {self.uuid}',
                task='alarm.set_alarm_off',
                crontab=schedule_turn_off_alarm,
                args=json.dumps([self.uuid])
            )

        else:
            on_crontab = self.turn_on_task.crontab
            off_crontab = self.turn_off_task.crontab

            on_crontab.minute = self.minute_start
            on_crontab.hour = self.hour_start
            on_crontab.day_of_week = cron_days

            off_crontab.minute = self.minute_end
            off_crontab.hour = self.hour_end
            off_crontab.day_of_week = cron_days

            on_crontab.save()
            off_crontab.save()

        super().save(*args, **kwargs)


class CameraMotionDetected(models.Model):
    class Meta:
        unique_together = ['event_ref', 'is_motion']

    created_at = models.DateTimeField(auto_now_add=True)
    device = models.ForeignKey(Device, on_delete=models.PROTECT)
    in_rectangle_roi = models.ManyToManyField(CameraRectangleROI, blank=True)

    event_ref = models.UUIDField()
    is_motion = models.BooleanField()


class CameraMotionDetectedPicture(models.Model):
    class Meta:
        unique_together = ['event_ref', 'is_motion']

    created_at = models.DateTimeField(auto_now_add=True)
    picture = models.ImageField(blank=True, null=True)
    device = models.ForeignKey(Device, on_delete=models.PROTECT)

    event_ref = models.UUIDField()
    is_motion = models.BooleanField()
