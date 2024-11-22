import os

from core.models import Course, SpacedRepetition, Student


def delete_temp_file(file_path):
    if os.path.isfile(file_path):
        os.remove(file_path)
        return True
    return False


def is_spaced_repetition_check(student_id, course_id, moment):
    student = Student.objects.get(id=student_id)
    course = Course.objects.get(id=course_id)
    spaced_repetition = SpacedRepetition.objects.filter(
        student=student, course=course
    ).first()
    if not spaced_repetition:
        return None
    spaced_repetition_update_completed_field(spaced_repetition, moment)
    return spaced_repetition


def spaced_repetition_update_completed_field(instance, moment_value):
    field_mapping = {
        1: "is_completed1",
        2: "is_completed2",
        3: "is_completed3",
    }
    if moment_value not in field_mapping:
        raise ValueError("Invalid moment. Must be 1, 2, or 3.")
    is_completed_field = field_mapping[moment_value]
    setattr(instance, is_completed_field, True)
    instance.save()
