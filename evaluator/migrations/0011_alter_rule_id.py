# Generated by Django 5.0.3 on 2024-06-20 13:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('evaluator', '0010_template_testset'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rule',
            name='id',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
    ]