# Generated by Django 3.2.4 on 2021-07-03 09:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('handler', '0019_remove_sales_due'),
    ]

    operations = [
        migrations.AddField(
            model_name='sales',
            name='currency',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='handler.currency'),
        ),
    ]
