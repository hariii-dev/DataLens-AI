from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Dataset
from .serializers import DatasetSerializer
from .services import analyze_dataset
from .cleaning import clean_dataset


class DatasetListCreateView(generics.ListCreateAPIView):
    serializer_class = DatasetSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        return Dataset.objects.filter(
            owner=self.request.user
        ).order_by('-created_at')

    def perform_create(self, serializer):
        dataset = serializer.save()
        try:
            analyze_dataset(dataset)
        except Exception:
            dataset.status = 'failed'
            dataset.save(update_fields=['status'])
            raise


class DatasetDetailView(generics.RetrieveDestroyAPIView):
    serializer_class = DatasetSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Dataset.objects.filter(owner=self.request.user)


class DatasetPreviewView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        dataset = generics.get_object_or_404(
            Dataset,
            pk=pk,
            owner=request.user
        )

        try:
            analysis = analyze_dataset(dataset)
            return Response(analysis)
        except Exception:
            return Response(
                {'error': 'Unable to analyze dataset.'},
                status=status.HTTP_400_BAD_REQUEST
            )


class DatasetCleanView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        dataset = generics.get_object_or_404(
            Dataset,
            pk=pk,
            owner=request.user
        )

        remove_duplicates = request.data.get(
            'remove_duplicates', True
        )
        fill_missing = request.data.get(
            'fill_missing', False
        )

        try:
            result = clean_dataset(
                dataset,
                remove_duplicates=remove_duplicates,
                fill_missing=fill_missing
            )
            return Response(result, status=status.HTTP_200_OK)

        except Exception:
            return Response(
                {'error': 'Unable to clean this dataset.'},
                status=status.HTTP_400_BAD_REQUEST
            )
