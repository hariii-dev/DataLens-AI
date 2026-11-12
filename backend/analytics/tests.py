import tempfile

from django.test import TestCase, override_settings
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient

from datasets.models import Dataset
from .models import AnalysisHistory


class AnalyticsAPITests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='analytics_test',
            password='TestPassword123!'
        )

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        self.media = tempfile.TemporaryDirectory()
        self.settings_override = override_settings(
            MEDIA_ROOT=self.media.name
        )
        self.settings_override.enable()

        self.dataset = Dataset.objects.create(
            owner=self.user,
            name='Test Dataset',
            file=SimpleUploadedFile(
                'test.csv',
                b'name,age,city\nArun,22,Chennai\nKumar,25,Madurai\n',
                content_type='text/csv'
            ),
            file_type='csv',
            file_size=60
        )

    def tearDown(self):
        self.settings_override.disable()
        self.media.cleanup()

    def test_generate_analytics(self):
        response = self.client.get(
            f'/api/analytics/{self.dataset.id}/'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['total_rows'], 2)
        self.assertIn('numeric_statistics', response.data)
        self.assertIn('chart_data', response.data)
        self.assertIn('age', response.data['chart_data'])

    def test_analysis_history_saved(self):
        self.client.get(f'/api/analytics/{self.dataset.id}/')

        self.assertEqual(
            AnalysisHistory.objects.filter(owner=self.user).count(),
            1
        )

    def test_analysis_history_delete(self):
        history = AnalysisHistory.objects.create(
            owner=self.user,
            dataset=self.dataset,
            result={'total_rows': 2}
        )

        response = self.client.delete(
            f'/api/analytics/history/{history.id}/'
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            AnalysisHistory.objects.filter(id=history.id).exists()
        )
