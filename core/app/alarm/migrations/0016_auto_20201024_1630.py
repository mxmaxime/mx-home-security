# Generated by Django 3.0.7 on 2020-10-24 16:30

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('alarm', '0015_alarmschedule_devices'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='alarmschedule',
            name='devices',
        ),
        migrations.AddField(
            model_name='alarmschedule',
            name='alarm_statuses',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, to='alarm.AlarmStatus'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='alarmschedule',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
    ]
