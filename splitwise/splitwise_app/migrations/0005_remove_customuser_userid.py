# Generated by Django 3.2.19 on 2023-10-15 17:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('splitwise_app', '0004_auto_20231015_2130'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='userId',
        ),
    ]
