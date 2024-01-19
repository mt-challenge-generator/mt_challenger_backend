# Generated by Django 4.2.5 on 2024-01-18 13:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('evaluator', '0004_remove_template_testset'),
    ]

    operations = [
        migrations.CreateModel(
            name='Engine',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=50)),
                ('engine_type', models.CharField(max_length=50)),
            ],
        ),
        migrations.AlterField(
            model_name='report',
            name='engine',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='evaluator.engine'),
        ),
    ]
