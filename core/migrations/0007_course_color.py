# Generated by Django 5.1 on 2024-11-05 19:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0006_remove_course_challenges_challenge_course"),
    ]

    operations = [
        migrations.AddField(
            model_name="course",
            name="color",
            field=models.CharField(default="#000000", max_length=7),
        ),
    ]