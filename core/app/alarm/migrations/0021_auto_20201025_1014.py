# Generated by Django 3.0.7 on 2020-10-25 10:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('alarm', '0020_cameramotiondetectedpicture_is_motion'),
    ]

    operations = [
        migrations.AddField(
            model_name='cameramotiondetected',
            name='is_motion',
            field=models.BooleanField(default=False),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='cameramotiondetected',
            name='event_ref',
            field=models.UUIDField(),
        ),
        migrations.AlterField(
            model_name='cameramotiondetectedpicture',
            name='event_ref',
            field=models.UUIDField(),
        ),
        migrations.AlterUniqueTogether(
            name='cameramotiondetected',
            unique_together={('event_ref', 'is_motion')},
        ),
        migrations.AlterUniqueTogether(
            name='cameramotiondetectedpicture',
            unique_together={('event_ref', 'is_motion')},
        ),
    ]