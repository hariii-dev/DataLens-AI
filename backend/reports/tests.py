import tempfile

from django.test import TestCase, override_settings
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient

from datasets.models import Dataset
from .models import Report


class ReportAPITests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='report_test',
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
            name='Report Test Dataset',
            file=SimpleUploadedFile(
                'test.csv',
                b'name,age\nArun,22\nKumar,25\n',
                content_type='text/csv'
            ),
            file_type='csv',
            file_size=27
        )

    def tearDown(self):
        self.settings_override.disable()
        self.media.cleanup()

    def test_generate_pdf_report(self):
        response = self.client.post(
            f'/api/reports/generate/{self.dataset.id}/'
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Report.objects.count(), 1)
        self.assertTrue(Report.objects.first().file.name.endswith('.pdf'))

    def test_list_reports(self):
        response = self.client.post(
            f'/api/reports/generate/{self.dataset.id}/'
        )

        self.assertEqual(response.status_code, 201)

        response = self.client.get('/api/reports/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
