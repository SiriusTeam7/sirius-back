"""
URL configuration for sirius project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token

from core.views import (
    ChallengeScoresView,
    ChallengeTemplateView,
    CompanyMetricsView,
    CourseSummaryView,
    GenerateChallengeView,
    GenerateFeedbackView,
    RegisterChallengeRatingView,
    RegisterEventChallengeView,
    SpacedRepetitionDetailView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("login/", obtain_auth_token, name="token_obtain"),
    path("api/courses-summary/", CourseSummaryView.as_view(), name="course-summary"),
    path(
        "api/register-event/",
        RegisterEventChallengeView.as_view(),
        name="register-event",
    ),
    path(
        "api/register_rating/",
        RegisterChallengeRatingView.as_view(),
        name="register-rating",
    ),
    path(
        "api/challenge_scores/<int:course_id>/",
        ChallengeScoresView.as_view(),
        name="challenge-scores",
    ),
    path(
        "api/get-challenge-by-id/<int:challenge_id>/",
        ChallengeTemplateView.as_view(),
        name="get-challenge-by-id",
    ),
    path(
        "api/spaced_repetition/",
        SpacedRepetitionDetailView.as_view(),
        name="spaced-repetition-detail",
    ),
    path("api/get-challenge/", GenerateChallengeView.as_view(), name="get-challenge"),
    path("api/get-feedback/", GenerateFeedbackView.as_view(), name="get-feedback"),
    path("api/company-metrics/", CompanyMetricsView.as_view(), name="company-metrics"),
]
