import os

from django.db.models import Avg, Count, Sum

from core.models import ChallengeStat, Course, SpacedRepetition, Student


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


def get_suggested_materials(course_id):
    suggestions = ""
    course = Course.objects.get(id=course_id)
    for material in course.materials.all():
        suggestions += f"{material.name}: {material.link}\n"
    return suggestions


def get_student_company_metrics(student_id):

    metrics = {}
    challenge_stats = ChallengeStat.objects.all()
    metrics["global"] = summarize_metrics(challenge_stats)

    company = Student.objects.get(id=student_id).company
    if company:
        challenge_stats = ChallengeStat.objects.filter(student__company_id=company.id)
        metrics["company"] = summarize_metrics(challenge_stats)

    return metrics


def summarize_metrics(challenge_stats):
    top_students = (
        challenge_stats.filter(score__gt=0)
        .values("student__name")
        .annotate(total_challenges=Count("id"))
        .order_by("-total_challenges")[:6]
    )
    average_scores_moment1 = challenge_stats.filter(moment=1).aggregate(
        average_score=Avg("score")
    )
    average_scores_moment2 = challenge_stats.filter(moment=2).aggregate(
        average_score=Avg("score")
    )
    average_scores_moment3 = challenge_stats.filter(moment=3).aggregate(
        average_score=Avg("score")
    )
    total_time = challenge_stats.filter(skipped=False).aggregate(
        total_time=Sum("challenge__estimated_minutes")
    )
    total_completed_challenges = challenge_stats.filter(score__gt=0).count()
    return {
        "top_students": top_students,
        "average_scores_moment1": average_scores_moment1 or 0,
        "average_scores_moment2": average_scores_moment2 or 0,
        "average_scores_moment3": average_scores_moment3 or 0,
        "total_time": total_time or 0,
        "total_completed_challenges": total_completed_challenges or 0,
    }
