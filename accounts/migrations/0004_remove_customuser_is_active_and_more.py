# Generated by Django 4.2.1 on 2023-07-18 16:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_remove_customuser_created_at'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='is_active',
        ),
        migrations.RemoveField(
            model_name='customuser',
            name='is_staff',
        ),
        migrations.RemoveField(
            model_name='customuser',
            name='is_superuser',
        ),
        migrations.RemoveField(
            model_name='customuser',
            name='updated_at',
        ),
    ]
