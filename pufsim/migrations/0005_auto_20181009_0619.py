# Generated by Django 2.0.4 on 2018-10-09 06:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pufsim', '0004_twobitflipanalyzer'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='TwoBitflipAnalyzer',
            new_name='ChallengePairAnalyzer',
        ),
    ]