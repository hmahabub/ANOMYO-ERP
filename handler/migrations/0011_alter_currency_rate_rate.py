# Generated by Django 3.2.4 on 2021-06-29 14:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('handler', '0010_auto_20210629_1438'),
    ]

    operations = [
        migrations.AlterField(
            model_name='currency_rate',
            name='rate',
            field=models.DecimalField(decimal_places=5, max_digits=13),
        ),
    ]