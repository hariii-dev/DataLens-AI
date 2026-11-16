from rest_framework import serializers
from .models import Dataset
from subscriptions.models import SubscriptionPlan, UserSubscription


class DatasetSerializer(serializers.ModelSerializer):

    class Meta:
        model = Dataset
        fields = [
            'id',
            'name',
            'file',
            'cleaned_file',
            'file_type',
            'file_size',
            'row_count',
            'column_count',
            'status',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'cleaned_file',
            'file_size',
            'row_count',
            'column_count',
            'status',
            'file_type',
            'created_at',
            'updated_at',
        ]

    def get_subscription(self):
        user = self.context['request'].user

        free_plan, _ = SubscriptionPlan.objects.get_or_create(
            name='Free',
            defaults={
                'price': 0,
                'max_datasets': 10,
                'max_upload_size_mb': 10,
                'ai_queries_per_month': 50,
            }
        )

        subscription, _ = UserSubscription.objects.get_or_create(
            user=user,
            defaults={'plan': free_plan}
        )

        return subscription

    def validate_file(self, value):
        extension = value.name.rsplit('.', 1)[-1].lower()

        if extension not in ['csv', 'xlsx']:
            raise serializers.ValidationError(
                'Only CSV and XLSX files are allowed.'
            )

        subscription = self.get_subscription()

        if subscription.status != 'active':
            raise serializers.ValidationError(
                'Your subscription is not active.'
            )

        plan = subscription.plan

        if value.size > plan.max_upload_size_mb * 1024 * 1024:
            raise serializers.ValidationError(
                f'Your {plan.name} plan allows maximum '
                f'{plan.max_upload_size_mb} MB per upload.'
            )

        dataset_count = Dataset.objects.filter(
            owner=self.context['request'].user
        ).count()

        if dataset_count >= plan.max_datasets:
            raise serializers.ValidationError(
                f'Your {plan.name} plan allows maximum '
                f'{plan.max_datasets} datasets.'
            )

        return value

    def create(self, validated_data):
        uploaded_file = validated_data['file']

        validated_data['file_type'] = (
            uploaded_file.name.rsplit('.', 1)[-1].lower()
        )
        validated_data['file_size'] = uploaded_file.size
        validated_data['owner'] = self.context['request'].user

        return super().create(validated_data)
