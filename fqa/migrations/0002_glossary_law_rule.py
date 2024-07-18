# Generated by Django 5.0.6 on 2024-07-18 01:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("fqa", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Glossary",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("terminology", models.CharField(max_length=100)),
                ("code", models.IntegerField()),
                ("content", models.TextField()),
                ("view", models.BigIntegerField(default=0)),
                ("week_view", models.BigIntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name="Law",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("law", models.CharField(max_length=100)),
                ("ministry", models.CharField(max_length=10)),
                ("code", models.CharField(max_length=20)),
                ("date", models.DateField()),
                ("content", models.TextField()),
                ("total_view", models.BigIntegerField(default=0)),
                ("week_view", models.BigIntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name="Rule",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("rule", models.CharField(max_length=100)),
                ("kind", models.CharField(max_length=20)),
                ("code", models.CharField(max_length=10)),
                ("state", models.CharField(max_length=20)),
                ("effective", models.DateField()),
                ("created", models.DateField()),
                ("content", models.TextField()),
                ("view", models.BigIntegerField(default=0)),
                ("week_view", models.BigIntegerField(default=0)),
            ],
        ),
    ]