# Generated by Django 5.2.4 on 2025-07-22 06:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('decisions', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='decision',
            name='date',
            field=models.DateField(blank=True, null=True),
        ),
    ]
