from django.test import TestCase
from rest_framework.test import APIClient
from subscriptions.models import UserSubscription


class RegistrationSubscriptionTest(TestCase):

    def test_new_user_gets_free_plan(self):
        client = APIClient()

        response = client.post(
            '/api/auth/register/',
            {
                'username': 'newuser_test',
                'email': 'newuser@example.com',
                'password': 'StrongPass@2026',
            },
            format='json'
        )

        self.assertEqual(response.status_code, 201)

        subscription = UserSubscription.objects.get(
            user__username='newuser_test'
        )

        self.assertEqual(subscription.plan.name, 'Free')
        self.assertEqual(subscription.status, 'active')
