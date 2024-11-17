# Generated by Django 5.1 on 2024-11-17 04:00

from django.db import migrations, models


def populate_name(apps, schema_editor):
    Challenge = apps.get_model("core", "Challenge")
    for challenge in Challenge.objects.all():
        if challenge.course and challenge.course.title:
            challenge.name = f"challenge {challenge.id} {challenge.course.title}"
        else:
            challenge.name = f"challenge {challenge.id} no_course"
        challenge.save()


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0007_course_color"),
    ]

    operations = [
        migrations.AddField(
            model_name="challenge",
            name="estimated_minutes",
            field=models.PositiveSmallIntegerField(default=10),
        ),
        migrations.AddField(
            model_name="challenge",
            name="name",
            field=models.CharField(max_length=240, null=True),
        ),
        migrations.RunPython(populate_name),
    ]