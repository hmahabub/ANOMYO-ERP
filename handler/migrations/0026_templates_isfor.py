# Generated by Django 3.2.4 on 2021-07-20 04:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('handler', '0025_auto_20210720_0951'),
    ]

    operations = [
        migrations.AddField(
            model_name='templates',
            name='isfor',
            field=models.CharField(default='invoice', max_length=40),
        ),
    ]
