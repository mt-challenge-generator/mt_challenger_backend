# Generated by Django 4.2.5 on 2023-12-18 13:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('evaluator', '0003_delete_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='template',
            name='testset',
        ),
    ]
