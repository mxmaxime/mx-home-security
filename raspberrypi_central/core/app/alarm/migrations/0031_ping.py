# Generated by Django 3.1.6 on 2021-02-15 14:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('alarm', '0030_auto_20210120_2156'),
    ]

    operations = [
        migrations.CreateModel(
            name='Ping',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('device_id', models.CharField(max_length=8)),
                ('service_name', models.CharField(max_length=100)),
                ('last_update', models.DateTimeField()),
            ],
            options={
                'unique_together': {('device_id', 'service_name')},
            },
        ),
    ]
