# Generated by Django 3.2 on 2021-06-20 14:01

from django.db import migrations, models
import utils.django.models


class Migration(migrations.Migration):

    dependencies = [
        ('automation', '0006_alter_automation_trigger_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='automation',
            name='trigger_name',
            field=utils.django.models.ChoiceArrayField(base_field=models.CharField(choices=[('ON_MOTION_DETECTED', 'on_motion_detected'), ('ON_MOTION_LEFT', 'on_motion_left'), ('ON_ALARM_OFF', 'on_alarm_off'), ('ON_ALARM_ON', 'on_alarm_on')], max_length=100), help_text='Any of these trigger names will trigger this automation to run.', size=None),
        ),
    ]
