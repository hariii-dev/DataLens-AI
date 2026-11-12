from django.shortcuts import get_object_or_404
from django.core.files.base import ContentFile

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from datasets.models import Dataset
from .models import Report
from .services import generate_pdf_report


class DatasetReportView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        dataset = get_object_or_404(
            Dataset,
            pk=pk,
            owner=request.user
        )

        try:
            pdf_buffer = generate_pdf_report(dataset)

            report = Report.objects.create(
                owner=request.user,
                dataset=dataset,
                title=f'{dataset.name} Analytics Report'
            )

            report.file.save(
                f'dataset_{dataset.id}_report.pdf',
                ContentFile(pdf_buffer.read()),
                save=True
            )

            return Response({
                'id': report.id,
                'title': report.title,
                'file': report.file.url,
                'created_at': report.created_at,
            }, status=status.HTTP_201_CREATED)

        except Exception:
            return Response(
                {'error': 'Unable to generate PDF report.'},
                status=status.HTTP_400_BAD_REQUEST
            )


class ReportListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        reports = Report.objects.filter(
            owner=request.user
        ).select_related('dataset')

        data = [
            {
                'id': report.id,
                'title': report.title,
                'dataset': report.dataset.name,
                'file': report.file.url,
                'created_at': report.created_at,
            }
            for report in reports
        ]

        return Response(data)
