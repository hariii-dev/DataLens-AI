import tempfile

from django.test import TestCase, override_settings
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from subscriptions.models import SubscriptionPlan, UserSubscription
from .models import Dataset


class DatasetAPITests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='dataset_test',
            password='TestPassword123!'
        )

        self.other_user = User.objects.create_user(
            username='other_test',
            password='TestPassword123!'
        )

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        self.media = tempfile.TemporaryDirectory()
        self.settings_override = override_settings(
            MEDIA_ROOT=self.media.name
        )
        self.settings_override.enable()

    def tearDown(self):
        self.settings_override.disable()
        self.media.cleanup()

    def create_dataset(self):
        return Dataset.objects.create(
            owner=self.user,
            name='Test Dataset',
            file=SimpleUploadedFile(
                'test.csv',
                b'name,age\nArun,22\nKumar,25\n',
                content_type='text/csv'
            ),
            file_type='csv',
            file_size=27
        )

    def test_dataset_list(self):
        self.create_dataset()

        response = self.client.get('/api/datasets/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)

    def test_user_cannot_access_other_dataset(self):
        dataset = Dataset.objects.create(
            owner=self.other_user,
            name='Private Dataset',
            file=SimpleUploadedFile(
                'private.csv',
                b'name\nArun\n',
                content_type='text/csv'
            ),
            file_type='csv',
            file_size=10
        )

        response = self.client.get(
            f'/api/datasets/{dataset.id}/'
        )

        self.assertEqual(response.status_code, 404)

    def test_dataset_delete(self):
        dataset = self.create_dataset()

        response = self.client.delete(
            f'/api/datasets/{dataset.id}/'
        )

        self.assertEqual(response.status_code, 204)
        self.assertFalse(
            Dataset.objects.filter(id=dataset.id).exists()
        )
    def test_free_plan_dataset_limit(self):
        free_plan = SubscriptionPlan.objects.create(
            name='Free',
            price=0,
            max_datasets=10,
            max_upload_size_mb=10,
            ai_queries_per_month=50
        )

        UserSubscription.objects.create(
            user=self.user,
            plan=free_plan
        )

        for number in range(10):
            Dataset.objects.create(
                owner=self.user,
                name=f'Dataset {number}',
                file=SimpleUploadedFile(
                    f'dataset{number}.csv',
                    b'name,age\nArun,22\n',
                    content_type='text/csv'
                ),
                file_type='csv',
                file_size=18
            )

        response = self.client.post(
            '/api/datasets/',
            {
                'name': 'Eleventh Dataset',
                'file': SimpleUploadedFile(
                    'eleventh.csv',
                    b'name,age\nKumar,25\n',
                    content_type='text/csv'
                )
            },
            format='multipart'
        )

        self.assertEqual(response.status_code, 400)

    def test_free_plan_upload_size_limit(self):
        free_plan = SubscriptionPlan.objects.create(
            name='Free',
            price=0,
            max_datasets=10,
            max_upload_size_mb=10,
            ai_queries_per_month=50
        )

        UserSubscription.objects.create(
            user=self.user,
            plan=free_plan
        )

        large_file = SimpleUploadedFile(
            'large.csv',
            b'a' * (10 * 1024 * 1024 + 1),
            content_type='text/csv'
        )

        response = self.client.post(
            '/api/datasets/',
            {
                'name': 'Large Dataset',
                'file': large_file
            },
            format='multipart'
        )

        self.assertEqual(response.status_code, 400)
