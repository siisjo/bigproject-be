# Generated by Django 5.0.6 on 2024-07-12 06:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("community", "0003_comment_updated_at"),
    ]

    operations = [
        migrations.DeleteModel(
            name="User",
        ),
    ]
