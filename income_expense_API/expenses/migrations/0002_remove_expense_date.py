# Generated by Django 4.2.6 on 2023-12-16 13:49

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("expenses", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="expense",
            name="date",
        ),
    ]
