# Generated by Django 3.0.6 on 2020-05-05 22:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='homemodel',
            name='active_cases',
        ),
        migrations.AddField(
            model_name='homemodel',
            name='state',
            field=models.TextField(default='Jharkhand'),
            preserve_default=False,
        ),
    ]
