# Generated by Django 4.2.5 on 2024-01-18 15:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('evaluator', '0006_report_engine_type_alter_report_engine_delete_engine'),
    ]

    operations = [
        migrations.AlterField(
            model_name='report',
            name='engine',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='report',
            name='engine_type',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
