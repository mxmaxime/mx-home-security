# Generated by Django 3.2 on 2021-06-20 14:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('devices', '0004_device_is_main'),
    ]

    operations = [
        migrations.AddField(
            model_name='device',
            name='mac_address',
            field=models.CharField(blank=True, default=None, max_length=32, null=True),
        ),
        migrations.AlterField(
            model_name='device',
            name='name',
            field=models.CharField(max_length=100, unique=True),
        ),
    ]
