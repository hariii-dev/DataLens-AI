from django.urls import path
from .views import DatasetReportView, ReportListView

urlpatterns = [
    path('', ReportListView.as_view(), name='report-list'),
    path('generate/<int:pk>/', DatasetReportView.as_view(), name='generate-report'),
]
