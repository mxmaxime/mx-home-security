# Generated by Django 3.1.6 on 2021-03-27 23:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('devices', '0004_device_is_main'),
        ('camera', '0006_cameramotionvideo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cameramotiondetected',
            name='device',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='camera_motions', to='devices.device'),
        ),
    ]
