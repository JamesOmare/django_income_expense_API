# Generated by Django 4.2.6 on 2023-12-26 08:49

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("income", "0001_initial"),
    ]

    operations = [
        migrations.RenameField(
            model_name="income",
            old_name="category",
            new_name="source",
        ),
    ]