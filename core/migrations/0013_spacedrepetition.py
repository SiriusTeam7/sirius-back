# Generated by Django 5.1 on 2024-11-22 16:48

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0012_material"),
    ]

    operations = [
        migrations.CreateModel(
            name="SpacedRepetition",
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
                ("moment1", models.DateTimeField()),
                ("is_completed1", models.BooleanField(default=False)),
                ("moment2", models.DateTimeField()),
                ("is_completed2", models.BooleanField(default=False)),
                ("moment3", models.DateTimeField()),
                ("is_completed3", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "course",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="spaced_repetitions",
                        to="core.course",
                    ),
                ),
                (
                    "student",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="spaced_repetitions",
                        to="core.student",
                    ),
                ),
            ],
        ),
    ]
