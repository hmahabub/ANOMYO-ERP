# Generated by Django 3.2.4 on 2021-07-24 05:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('handler', '0029_auto_20210723_1809'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee_info',
            name='face',
            field=models.ImageField(default='default/avatar.png', upload_to='employee'),
        ),
        migrations.AddField(
            model_name='user_info',
            name='face',
            field=models.ImageField(default='default/avatar.png', upload_to='user'),
        ),
        migrations.AlterField(
            model_name='company',
            name='logo',
            field=models.ImageField(default='deafult/logo.jpg', upload_to='logo'),
        ),
    ]
