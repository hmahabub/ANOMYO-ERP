# Generated by Django 3.2.4 on 2021-07-03 08:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('handler', '0018_client_info_lead'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sales',
            name='due',
        ),
    ]
