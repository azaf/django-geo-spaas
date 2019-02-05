# Generated by Django 2.1.5 on 2019-02-05 15:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('viewer', '0006_auto_20190204_1345'),
    ]

    operations = [
        migrations.AlterField(
            model_name='search',
            name='instrument',
            field=models.ManyToManyField(blank=True, default=None, to='vocabularies.Instrument'),
        ),
        migrations.AlterField(
            model_name='search',
            name='parameter',
            field=models.ManyToManyField(blank=True, default=None, to='vocabularies.Parameter'),
        ),
        migrations.AlterField(
            model_name='search',
            name='platform',
            field=models.ManyToManyField(blank=True, default=None, to='vocabularies.Platform'),
        ),
    ]
