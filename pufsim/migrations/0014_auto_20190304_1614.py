# Generated by Django 2.1.3 on 2019-03-04 16:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pufsim', '0013_biastester'),
    ]

    operations = [
        migrations.AlterField(
            model_name='biastester',
            name='puf_type',
            field=models.ForeignKey(limit_choices_to=models.Q(models.Q(('app_label', 'pufsim'), ('model', 'pufgenerator')), models.Q(('app_label', 'pufsim'), ('model', 'compositepufgenerator')), _connector='OR'), on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType'),
        ),
    ]
