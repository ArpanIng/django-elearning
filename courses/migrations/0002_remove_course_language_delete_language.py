# Generated by Django 4.2.13 on 2024-06-16 16:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("courses", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="course",
            name="language",
        ),
        migrations.DeleteModel(
            name="Language",
        ),
    ]
