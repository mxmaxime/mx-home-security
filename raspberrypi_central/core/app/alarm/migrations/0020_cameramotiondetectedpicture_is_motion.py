# Generated by Django 3.0.7 on 2020-10-25 09:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('alarm', '0019_auto_20201024_1839'),
    ]

    operations = [
        migrations.AddField(
            model_name='cameramotiondetectedpicture',
            name='is_motion',
            field=models.BooleanField(default=True),
            preserve_default=False,
        ),
    ]