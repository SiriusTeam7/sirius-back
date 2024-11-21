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

from core.views import (
    AddCourseToStudentView,
    ChallengeTemplateView,
    CourseSummaryView,
    GenerateChallengeView,
    GenerateFeedbackView,
    LoginView,
    LogoutView,
    PromptTemplateView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("api/prompts/", PromptTemplateView.as_view(), name="prompt-templates"),
    path(
        "api/add-course-to-student/",
        AddCourseToStudentView.as_view(),
        name="add-course-to-student",
    ),
    path("api/courses-summary/", CourseSummaryView.as_view(), name="course-summary"),
    path(
        "api/get-challenge-by-id/<int:challenge_id>/",
        ChallengeTemplateView.as_view(),
        name="get-challenge-by-id",
    ),
    path("api/get-challenge/", GenerateChallengeView.as_view(), name="get-challenge"),
    path("api/get-feedback/", GenerateFeedbackView.as_view(), name="get-feedback"),
]
