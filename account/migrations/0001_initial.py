# Generated by Django 5.0.6 on 2024-07-01 00:55

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('nationality', models.CharField(max_length=50)),
                ('work_at', models.CharField(max_length=50)),
                ('uuid', models.CharField(max_length=36, unique=True)),
                ('username', models.CharField(max_length=50)),
                ('nickname', models.CharField(max_length=20, unique=True)),
                ('password', models.CharField(max_length=60)),
                ('email', models.EmailField(max_length=100, unique=True)),
                ('role', models.BooleanField(default=False)),
                ('profile_picture', models.CharField(blank=True, max_length=255, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'user',
            },
        ),
    ]
