from django.db import models
from django.contrib.auth.models import User
from datasets.models import Dataset


class AnalysisHistory(models.Model):
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='analysis_history'
    )
    dataset = models.ForeignKey(
        Dataset,
        on_delete=models.CASCADE,
        related_name='analysis_history'
    )
    result = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.dataset.name} - Analysis'
