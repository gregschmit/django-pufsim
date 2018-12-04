# Generated by Django 2.1.3 on 2018-11-20 15:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pufsim', '0006_neighborpredictor'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='neighborpredictor',
            name='group',
        ),
        migrations.RemoveField(
            model_name='neighborpredictor',
            name='match_range',
        ),
        migrations.AddField(
            model_name='neighborpredictor',
            name='k',
            field=models.IntegerField(default=1),
        ),
        migrations.AlterField(
            model_name='neighborpredictor',
            name='known_set_limit',
            field=models.IntegerField(default=2, help_text='The predictor will iterate over `n` from `k` to `known_set_limit`, where `n` is the known set size that we use to predict the next challenge.'),
        ),
    ]