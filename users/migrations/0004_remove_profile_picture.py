# Generated by Django 2.2.11 on 2020-05-16 03:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_profile_picture'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='picture',
        ),
    ]
