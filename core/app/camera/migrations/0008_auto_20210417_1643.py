# Generated by Django 3.2 on 2021-04-17 16:43

from django.db import migrations


def delete_all(apps, schema_editor):
    CameraMotionVideo = apps.get_model('camera', 'CameraMotionVideo')
    CameraMotionVideo.objects.all().delete()

class Migration(migrations.Migration):

    dependencies = [
        ('camera', '0007_auto_20210327_2327'),
    ]

    operations = [
        migrations.RunPython(delete_all)
    ]
