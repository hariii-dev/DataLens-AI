from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        validators=[validate_password]
    )

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']

    def create(self, validated_data):
        from subscriptions.models import SubscriptionPlan, UserSubscription

        user = User.objects.create_user(**validated_data)

        free_plan, created = SubscriptionPlan.objects.get_or_create(
    name='Free',
    defaults={
        'price': 0,
        'max_datasets': 5,
        'max_upload_size_mb': 10,
        'ai_queries_per_month': 50,
    }
)

        UserSubscription.objects.create(
            user=user,
            plan=free_plan
        )

        return user
