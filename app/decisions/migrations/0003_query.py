# Generated by Django 5.2.4 on 2025-07-24 21:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('decisions', '0002_decision_date'),
    ]

    operations = [
        migrations.CreateModel(
            name='Query',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('string', models.TextField()),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
