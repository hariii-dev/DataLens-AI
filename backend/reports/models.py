from django.db import models
from django.contrib.auth.models import User
from datasets.models import Dataset


class Report(models.Model):
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reports'
    )
    dataset = models.ForeignKey(
        Dataset,
        on_delete=models.CASCADE,
        related_name='reports'
    )
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='reports/')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title
