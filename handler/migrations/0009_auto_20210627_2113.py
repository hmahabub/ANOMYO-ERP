# Generated by Django 3.2.4 on 2021-06-27 15:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('handler', '0008_auto_20210627_1452'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='currency_rate',
            name='month',
        ),
        migrations.RemoveField(
            model_name='currency_rate',
            name='time',
        ),
        migrations.AddField(
            model_name='currency_rate',
            name='year',
            field=models.CharField(choices=[(2005, 2005), (2006, 2006), (2007, 2007), (2008, 2008), (2009, 2009), (2010, 2010), (2011, 2011), (2012, 2012), (2013, 2013), (2014, 2014), (2015, 2015), (2016, 2016), (2017, 2017), (2018, 2018), (2019, 2019), (2020, 2020)], default=2021, max_length=5),
        ),
    ]