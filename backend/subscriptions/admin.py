from django.contrib import admin
from .models import SubscriptionPlan, UserSubscription


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'price',
        'max_datasets',
        'max_upload_size_mb',
        'ai_queries_per_month',
        'is_active',
    )
    list_filter = ('is_active',)
    search_fields = ('name',)


@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'plan',
        'status',
        'started_at',
        'expires_at',
    )
    list_filter = ('status', 'plan')
    search_fields = ('user__username',)
