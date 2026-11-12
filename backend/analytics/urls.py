from django.urls import path
from .views import (
    DatasetAnalyticsView,
    AnalysisHistoryView,
    AnalysisHistoryDeleteView,
)

urlpatterns = [
    path('', AnalysisHistoryView.as_view(), name='analysis-history'),
    path('<int:pk>/', DatasetAnalyticsView.as_view(), name='dataset-analytics'),
    path('history/<int:pk>/', AnalysisHistoryDeleteView.as_view(), name='analysis-history-delete'),
]
