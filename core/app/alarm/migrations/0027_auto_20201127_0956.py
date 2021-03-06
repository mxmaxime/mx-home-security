# Generated by Django 3.0.7 on 2020-11-27 09:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('alarm', '0026_camerarectangleroi_disabled'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='camerarectangleroi',
            options={'default_manager_name': 'objects'},
        ),
        migrations.RemoveField(
            model_name='alarmschedule',
            name='alarm_statuses',
        ),
        migrations.AddField(
            model_name='alarmschedule',
            name='alarm_statuses',
            field=models.ManyToManyField(related_name='alarm_schedules', to='alarm.AlarmStatus'),
        ),
    ]
