# Generated by Django 3.0.7 on 2020-09-14 15:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('devices', '0002_auto_20200731_2128'),
        ('alarm', '0006_auto_20200809_1008'),
    ]

    operations = [
        migrations.AddField(
            model_name='alarmstatus',
            name='device',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, to='devices.Device'),
            preserve_default=False,
        ),
    ]