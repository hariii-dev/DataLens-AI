from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient

from .models import SubscriptionPlan, UserSubscription


class SubscriptionAPITests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='subscription_test',
            password='TestPassword123!'
        )

        self.plan = SubscriptionPlan.objects.create(
            name='Free',
            price=0,
            max_datasets=5,
            max_upload_size_mb=10,
            ai_queries_per_month=50,
        )

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_list_active_plans(self):
        response = self.client.get('/api/subscriptions/plans/')

        self.assertEqual(response.status_code, 200)
        plan_names = [item['name'] for item in response.data['results']]
        self.assertIn('Free', plan_names)

    def test_my_subscription(self):
        UserSubscription.objects.create(
            user=self.user,
            plan=self.plan
        )

        response = self.client.get(
            '/api/subscriptions/my-subscription/'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['plan']['name'], 'Free')

    def test_user_without_subscription(self):
        response = self.client.get(
            '/api/subscriptions/my-subscription/'
        )

        self.assertEqual(response.status_code, 404)
