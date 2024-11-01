from django.contrib import admin
from core.models import PromptTemplate


class PromptTemplateAdmin(admin.ModelAdmin):
    model = PromptTemplate
    list_display = ("type", "created_at", "updated_at")


admin.site.register(PromptTemplate, PromptTemplateAdmin)
