# Generated by Django 3.0.7 on 2021-01-21 13:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('camera', '0002_auto_20210120_2156'),
    ]

    operations = [
        migrations.AddField(
            model_name='cameramotiondetected',
            name='motion_ended_picture',
            field=models.ImageField(blank=True, null=True, upload_to=''),
        ),
        migrations.AddField(
            model_name='cameramotiondetected',
            name='motion_started_picture',
            field=models.ImageField(default='', upload_to=''),
            preserve_default=False,
        ),
        migrations.DeleteModel(
            name='CameraMotionDetectedPicture',
        ),
    ]
