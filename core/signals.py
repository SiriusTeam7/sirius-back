from datetime import timedelta

from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.utils.timezone import now

from .models import SpacedRepetition, Student


@receiver(m2m_changed, sender=Student.courses.through)
def create_spaced_repetition(sender, instance, action, reverse, pk_set, **kwargs):
    """
    Signal to create SpacedRepetition records when courses are added to a student.
    """
    if action == "post_add":
        student = instance

        for course_id in pk_set:
            course = student.courses.get(id=course_id)
            if not SpacedRepetition.objects.filter(
                student=student, course=course
            ).exists():
                # Create the SpacedRepetition record
                SpacedRepetition.objects.create(
                    student=student,
                    course=course,
                    moment1=now() + timedelta(days=1),
                    moment2=now() + timedelta(weeks=1),
                    moment3=now() + timedelta(days=30),
                )
