from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from datasets.models import Dataset
from .models import AnalysisHistory
from .services import generate_analytics


class DatasetAnalyticsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        dataset = get_object_or_404(
            Dataset,
            pk=pk,
            owner=request.user
        )

        try:
            result = generate_analytics(dataset)

            AnalysisHistory.objects.create(
                owner=request.user,
                dataset=dataset,
                result=result
            )

            return Response(result)

        except Exception:
            return Response(
                {'error': 'Unable to generate analytics.'},
                status=status.HTTP_400_BAD_REQUEST
            )


class AnalysisHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        history = AnalysisHistory.objects.filter(
            owner=request.user
        ).select_related('dataset')

        data = [
            {
                'id': item.id,
                'dataset_id': item.dataset.id,
                'dataset_name': item.dataset.name,
                'result': item.result,
                'created_at': item.created_at,
            }
            for item in history
        ]

        return Response(data)


class AnalysisHistoryDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        history = get_object_or_404(
            AnalysisHistory,
            pk=pk,
            owner=request.user
        )

        history.delete()

        return Response(
            {'message': 'Analysis history deleted successfully.'},
            status=status.HTTP_200_OK
        )
