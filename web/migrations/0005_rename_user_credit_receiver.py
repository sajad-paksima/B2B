# Generated by Django 4.2.4 on 2023-08-08 17:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("web", "0004_token"),
    ]

    operations = [
        migrations.RenameField(
            model_name="credit",
            old_name="user",
            new_name="receiver",
        ),
    ]
