# Generated by Django 3.0.7 on 2020-08-02 17:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('house', '0005_telegrambotchatid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='telegrambotchatid',
            name='chat_id',
            field=models.CharField(max_length=60),
        ),
    ]
