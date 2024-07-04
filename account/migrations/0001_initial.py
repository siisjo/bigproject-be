# Generated by Django 5.0.6 on 2024-07-04 01:37

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="User",
            fields=[
                (
                    "last_login",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="last login"
                    ),
                ),
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("nationality", models.CharField(max_length=50)),
                ("work_at", models.CharField(max_length=50)),
                (
                    "uuid",
                    models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
                ),
                ("username", models.CharField(max_length=50)),
                ("nickname", models.CharField(max_length=20, unique=True)),
                ("password", models.CharField(max_length=128)),
                ("email", models.EmailField(max_length=100, unique=True)),
                (
                    "profile_picture",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("is_active", models.BooleanField(default=True)),
                ("is_staff", models.BooleanField(default=False)),
                ("is_superuser", models.BooleanField(default=False)),
            ],
            options={
                "db_table": "user",
            },
        ),
    ]
