from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('datetime', models.DateTimeField(auto_now_add=True)),
                ('status', models.BooleanField(default=False)),
                ('description', models.TextField(blank=True, null=True)),
            ],
        ),
    ]
