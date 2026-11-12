from django.urls import path
from .views import (
    DatasetListCreateView,
    DatasetDetailView,
    DatasetPreviewView,
    DatasetCleanView,
)

urlpatterns = [
    path('', DatasetListCreateView.as_view(), name='dataset-list-create'),
    path('<int:pk>/', DatasetDetailView.as_view(), name='dataset-detail'),
    path('<int:pk>/preview/', DatasetPreviewView.as_view(), name='dataset-preview'),
    path('<int:pk>/clean/', DatasetCleanView.as_view(), name='dataset-clean'),
]
