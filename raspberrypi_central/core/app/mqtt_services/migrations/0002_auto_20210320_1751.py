# Generated by Django 3.1.6 on 2021-03-20 17:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mqtt_services', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='mqttservicesconnectionstatuslogs',
            options={'get_latest_by': 'created_at'},
        ),
    ]
