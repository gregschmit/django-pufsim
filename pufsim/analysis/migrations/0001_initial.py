# Generated by Django 2.2.1 on 2019-06-12 15:38

from django.db import migrations, models
import django.db.models.deletion
import gfklookupwidget.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('pufsim', '0001_initial'),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='NeighborPredictor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('progress', models.IntegerField(default=0, editable=False)),
                ('data', models.TextField(blank=True, editable=False)),
                ('pid', models.IntegerField(default=0, editable=False)),
                ('k', models.IntegerField(default=1, help_text='0 for choose all')),
                ('distance', models.TextField(choices=[('gamma', 'gamma'), ('hamming', 'hamming')], default='gamma', max_length=30)),
                ('known_set_limit', models.IntegerField(default=2, help_text='The predictor will iterate over `n` from `k` to `known_set_limit`, where `n` is the known set size that we use to predict the next challenge.')),
                ('number_of_pufs', models.IntegerField(default=100)),
                ('iterations_per_puf', models.IntegerField(default=100)),
                ('hop_by_power_of_two', models.BooleanField(default=False, help_text='Bins go from K to known_set_limit, if this option is checked, then go from 2^(K-1) to 2^(known_set_limit).')),
                ('puf_generator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pufsim.PUFGenerator')),
            ],
            options={
                'verbose_name': 'Neighbor Predictor',
            },
        ),
        migrations.CreateModel(
            name='ChallengePairAnalyzer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('progress', models.IntegerField(default=0, editable=False)),
                ('data', models.TextField(blank=True, editable=False)),
                ('pid', models.IntegerField(default=0, editable=False)),
                ('base_challenge', models.IntegerField(default=0, help_text='Enter the challenge as a decimal value and the system will truncate or add zeros to the most significant bit side (e.g., 12 will be converted to 1100 and then padded to 001100 if the PUF has 6 stages)')),
                ('test_challenge', models.IntegerField(default=0, help_text='Enter the challenge as a decimal value and the system will truncate or add zeros to the most significant bit side (e.g., 12 will be converted to 1100 and then padded to 001100 if the PUF has 6 stages)')),
                ('number_of_pufs', models.IntegerField(default=100)),
                ('puf_generator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pufsim.PUFGenerator')),
            ],
            options={
                'verbose_name': 'Challenge Pair Analyzer',
            },
        ),
        migrations.CreateModel(
            name='BitflipAnalyzer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('progress', models.IntegerField(default=0, editable=False)),
                ('data', models.TextField(blank=True, editable=False)),
                ('pid', models.IntegerField(default=0, editable=False)),
                ('base_challenge', models.IntegerField(default=0, help_text='Enter the challenge as a decimal value and the system will truncate or add zeros to the most significant bit side (e.g., 12 will be converted to 1100 and then padded to 001100 if the PUF has 6 stages)')),
                ('number_of_pufs', models.IntegerField(default=100)),
                ('puf_generator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pufsim.PUFGenerator', verbose_name='PUF generator')),
            ],
            options={
                'verbose_name': 'Bitflip Analyzer',
            },
        ),
        migrations.CreateModel(
            name='BiasTester',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('progress', models.IntegerField(default=0, editable=False)),
                ('data', models.TextField(blank=True, editable=False)),
                ('pid', models.IntegerField(default=0, editable=False)),
                ('puf_id', gfklookupwidget.fields.GfkLookupField()),
                ('number_of_pufs', models.IntegerField(default=100)),
                ('n', models.IntegerField(default=100, help_text='How many samples to get for each PUF')),
                ('puf_type', models.ForeignKey(limit_choices_to=models.Q(models.Q(('app_label', 'pufsim'), ('model', 'pufgenerator')), models.Q(('app_label', 'pufsim'), ('model', 'compositepufgenerator')), _connector='OR'), on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType')),
            ],
            options={
                'verbose_name': 'Bias Tester',
            },
        ),
    ]