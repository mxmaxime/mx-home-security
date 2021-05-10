# Generated by Django 3.2 on 2021-05-10 21:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('automation', '0002_alter_actionmqttpublish_automation'),
    ]

    operations = [
        migrations.AddField(
            model_name='mqttclient',
            name='password',
            field=models.CharField(blank=True, default=None, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='mqttclient',
            name='username',
            field=models.CharField(default='mx', max_length=50),
            preserve_default=False,
        ),
    ]
