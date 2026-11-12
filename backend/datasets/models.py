from django.db import models
from django.contrib.auth.models import User


def dataset_upload_path(instance, filename):
    return f"datasets/user_{instance.owner.id}/{filename}"


def cleaned_upload_path(instance, filename):
    return f"cleaned/user_{instance.owner.id}/{filename}"


class Dataset(models.Model):
    STATUS_CHOICES = [
        ('uploaded', 'Uploaded'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='datasets'
    )
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to=dataset_upload_path)
    cleaned_file = models.FileField(
        upload_to=cleaned_upload_path,
        blank=True,
        null=True
    )
    file_type = models.CharField(max_length=10)
    file_size = models.BigIntegerField(default=0)
    row_count = models.PositiveIntegerField(default=0)
    column_count = models.PositiveIntegerField(default=0)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='uploaded'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
