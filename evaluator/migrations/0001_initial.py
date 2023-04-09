# Generated by Django 4.2 on 2023-04-03 23:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
            ],
            options={
                'verbose_name_plural': 'Categories',
            },
        ),
        migrations.CreateModel(
            name='Langpair',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='Language',
            fields=[
                ('code', models.CharField(max_length=8, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='Phenomenon',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='evaluator.category')),
            ],
            options={
                'verbose_name_plural': 'Phenomena',
            },
        ),
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('legacy_id', models.SmallIntegerField(blank=True, null=True)),
                ('client', models.CharField(max_length=50)),
                ('comment', models.CharField(max_length=100)),
                ('created_time', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Template',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('legacy_id', models.SmallIntegerField(blank=True, null=True)),
                ('description', models.CharField(blank=True, max_length=50)),
                ('select', models.DecimalField(decimal_places=2, max_digits=10)),
                ('scramble_factor', models.DecimalField(decimal_places=1, max_digits=5)),
                ('created_time', models.DateTimeField(auto_now_add=True)),
                ('phenomena', models.ManyToManyField(to='evaluator.phenomenon')),
            ],
        ),
        migrations.CreateModel(
            name='TestItem',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('legacy_id', models.CharField(max_length=10)),
                ('legacy_testpoint', models.SmallIntegerField()),
                ('legacy_version', models.SmallIntegerField()),
                ('source_sentence', models.CharField(max_length=500)),
                ('comment', models.CharField(max_length=100)),
                ('created_time', models.DateTimeField(auto_now_add=True)),
                ('phenomenon', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='evaluator.phenomenon')),
            ],
        ),
        migrations.CreateModel(
            name='Translation',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('legacy_id', models.CharField(blank=True, max_length=10)),
                ('sentence', models.CharField(max_length=500)),
                ('label', models.IntegerField(choices=[(1, 'Pass'), (2, 'Fail'), (3, 'Warning')], default=3)),
                ('report', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='evaluator.report')),
                ('test_item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='evaluator.testitem')),
            ],
        ),
        migrations.CreateModel(
            name='Testset',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=40)),
                ('description', models.CharField(max_length=250)),
                ('langpair', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='evaluator.langpair')),
            ],
        ),
        migrations.AddField(
            model_name='testitem',
            name='testset',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='evaluator.testset'),
        ),
        migrations.CreateModel(
            name='TemplatePosition',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pos', models.IntegerField()),
                ('template', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='evaluator.template')),
                ('test_item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='evaluator.testitem')),
            ],
        ),
        migrations.AddField(
            model_name='template',
            name='testset',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='evaluator.testset'),
        ),
        migrations.CreateModel(
            name='Rule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('string', models.CharField(max_length=200)),
                ('regex', models.BooleanField(default=True)),
                ('positive', models.BooleanField(default=True)),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='evaluator.testitem')),
            ],
        ),
        migrations.AddField(
            model_name='report',
            name='template',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='evaluator.template'),
        ),
        migrations.AddField(
            model_name='langpair',
            name='source_language',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='source_language', to='evaluator.language'),
        ),
        migrations.AddField(
            model_name='langpair',
            name='target_language',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='target_language', to='evaluator.language'),
        ),
        migrations.CreateModel(
            name='Distractor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=500)),
                ('language', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='evaluator.language')),
            ],
        ),
    ]
