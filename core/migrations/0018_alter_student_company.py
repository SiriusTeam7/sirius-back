# Generated by Django 5.1 on 2024-11-23 06:37

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0017_challengestat_moment"),
    ]

    operations = [
        migrations.AlterField(
            model_name="student",
            name="company",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="students",
                to="core.company",
            ),
        ),
    ]