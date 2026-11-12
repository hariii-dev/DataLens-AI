import tempfile

from django.test import TestCase, override_settings
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient

from datasets.models import Dataset
from .models import AIConversation, AIMessage


class AIConversationTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='ai_test',
            password='TestPassword123!'
        )
        self.other_user = User.objects.create_user(
            username='other_ai',
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
            name='AI Test Dataset',
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

    def test_create_conversation(self):
        response = self.client.post(
            '/api/ai/conversations/',
            {'dataset': self.dataset.id},
            format='json'
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(AIConversation.objects.count(), 1)

    def test_chat_creates_user_message(self):
        conversation = AIConversation.objects.create(
            owner=self.user,
            dataset=self.dataset
        )

        response = self.client.post(
            f'/api/ai/conversations/{conversation.id}/chat/',
            {'question': 'What is the average age?'},
            format='json'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(AIMessage.objects.count(), 1)
        self.assertEqual(response.data['ai_status'], 'awaiting_provider')

    def test_user_cannot_access_other_conversation(self):
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

        conversation = AIConversation.objects.create(
            owner=self.other_user,
            dataset=dataset
        )

        response = self.client.post(
            f'/api/ai/conversations/{conversation.id}/chat/',
            {'question': 'Show data'},
            format='json'
        )

        self.assertEqual(response.status_code, 404)
