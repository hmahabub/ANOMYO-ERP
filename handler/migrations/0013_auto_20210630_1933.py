# Generated by Django 3.2.4 on 2021-06-30 13:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('handler', '0012_auto_20210630_1148'),
    ]

    operations = [
        migrations.CreateModel(
            name='department',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='payroll_full',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('attendance', models.IntegerField(default=0)),
                ('basic', models.DecimalField(decimal_places=2, default=0, max_digits=9)),
                ('medical', models.DecimalField(decimal_places=2, default=0, max_digits=9)),
                ('home', models.DecimalField(decimal_places=2, default=0, max_digits=9)),
                ('conveyance', models.DecimalField(decimal_places=2, default=0, max_digits=9)),
                ('transport', models.DecimalField(decimal_places=2, default=0, max_digits=9)),
                ('others', models.DecimalField(decimal_places=2, default=0, max_digits=9)),
                ('deduction', models.DecimalField(decimal_places=2, default=0, max_digits=9)),
                ('advance', models.DecimalField(decimal_places=2, default=0, max_digits=9)),
                ('editable', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='payroll_part',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('work_hours', models.IntegerField(default=0)),
                ('hours_rate', models.DecimalField(decimal_places=3, max_digits=9)),
                ('others', models.DecimalField(decimal_places=2, default=0, max_digits=9)),
                ('advance', models.DecimalField(decimal_places=2, default=0, max_digits=9)),
                ('editable', models.BooleanField(default=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='salary',
            name='currency',
        ),
        migrations.RemoveField(
            model_name='salary',
            name='employee',
        ),
        migrations.RenameField(
            model_name='employee_info',
            old_name='role',
            new_name='designation',
        ),
        migrations.RemoveField(
            model_name='employee_info',
            name='department',
        ),
        migrations.RemoveField(
            model_name='employee_info',
            name='id_no',
        ),
        migrations.RemoveField(
            model_name='month',
            name='is_open',
        ),
        migrations.AlterField(
            model_name='company',
            name='invoice_template',
            field=models.IntegerField(default=1),
        ),
        migrations.AlterField(
            model_name='company',
            name='payroll_template',
            field=models.IntegerField(default=1),
        ),
        migrations.DeleteModel(
            name='payroll',
        ),
        migrations.DeleteModel(
            name='salary',
        ),
        migrations.AddField(
            model_name='payroll_part',
            name='month',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='handler.month'),
        ),
        migrations.AddField(
            model_name='payroll_full',
            name='employee',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='handler.employee_info'),
        ),
        migrations.AddField(
            model_name='payroll_full',
            name='month',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='handler.month'),
        ),
        migrations.AddField(
            model_name='employee_info',
            name='dept',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='handler.department'),
        ),
    ]
