# Generated by Django 5.0.3 on 2024-04-18 19:17

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('evaluator', '0009_alter_testitem_legacy_id_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='template',
            name='testset',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='evaluator.testset'),
            preserve_default=False,
        ),
    ]
