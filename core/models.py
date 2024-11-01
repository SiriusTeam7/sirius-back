from django.db import models


class PromptTemplate(models.Model):
    PROMPT_TYPE_CHOICES = (
        ("CH", "Challenge"),
        ("FE", "Feedback"),
        ("CO", "Config"),
    )
    type = models.CharField(max_length=12, choices=PROMPT_TYPE_CHOICES)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
