# Generated by Django 4.2.5 on 2024-01-18 13:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('evaluator', '0005_engine_alter_report_engine'),
    ]

    operations = [
        migrations.AddField(
            model_name='report',
            name='engine_type',
            field=models.CharField(default=1, max_length=50),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='report',
            name='engine',
            field=models.CharField(max_length=50),
        ),
        migrations.DeleteModel(
            name='Engine',
        ),
    ]
