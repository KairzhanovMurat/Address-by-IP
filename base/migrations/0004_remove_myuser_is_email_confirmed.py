# Generated by Django 4.1.2 on 2022-10-14 20:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0003_myuser_is_email_confirmed'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='myuser',
            name='is_email_confirmed',
        ),
    ]
