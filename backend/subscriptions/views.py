from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from .models import SubscriptionPlan, UserSubscription
from .serializers import (
    SubscriptionPlanSerializer,
    UserSubscriptionSerializer,
)


class SubscriptionPlanListView(generics.ListAPIView):
    serializer_class = SubscriptionPlanSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return SubscriptionPlan.objects.filter(
            is_active=True
        ).order_by('price')


class MySubscriptionView(generics.RetrieveAPIView):
    serializer_class = UserSubscriptionSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return get_object_or_404(
            UserSubscription.objects.select_related('plan'),
            user=self.request.user
        )
