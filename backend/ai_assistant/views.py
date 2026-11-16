from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
import logging

from datasets.models import Dataset
from .models import AIConversation, AIMessage
from .serializers import AIConversationSerializer, AIMessageSerializer
from .services import (
    build_dataset_context,
    build_ai_prompt,
    generate_ai_response
)

logger = logging.getLogger(__name__)


class AIConversationListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        conversations = AIConversation.objects.filter(
            owner=request.user
        ).select_related('dataset')

        return Response(
            AIConversationSerializer(conversations, many=True).data
        )

    def post(self, request):
        dataset = get_object_or_404(
            Dataset,
            pk=request.data.get('dataset'),
            owner=request.user
        )

        conversation = AIConversation.objects.create(
            owner=request.user,
            dataset=dataset,
            title=request.data.get('title', 'New Conversation')
        )

        return Response(
            AIConversationSerializer(conversation).data,
            status=status.HTTP_201_CREATED
        )


class AIChatView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        conversation = get_object_or_404(
            AIConversation,
            pk=pk,
            owner=request.user
        )

        question = request.data.get('question', '')

        if not isinstance(question, str):
            return Response(
                {'error': 'Question must be text.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        question = question.strip()

        if not question:
            return Response(
                {'error': 'Question is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if len(question) > 2000:
            return Response(
                {'error': 'Question cannot exceed 2000 characters.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            context = build_dataset_context(conversation.dataset)
            prompt = build_ai_prompt(question, context)

        except Exception:
            logger.exception('Dataset context preparation failed.')
            return Response(
                {'error': 'Unable to prepare dataset context.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            answer = generate_ai_response(prompt)

        except Exception:
            logger.exception('Gemini response generation failed.')
            return Response(
                {'error': 'AI service is temporarily unavailable.'},
                status=status.HTTP_502_BAD_GATEWAY
            )

        if not conversation.messages.filter(role="user").exists():
            conversation.title = (
                question[:47] + "..." if len(question) > 50 else question
            )

        user_message = AIMessage.objects.create(
            conversation=conversation,
            role='user',
            content=question
        )

        assistant_message = AIMessage.objects.create(
            conversation=conversation,
            role='assistant',
            content=answer
        )

        conversation.save(update_fields=['title', 'updated_at'])

        return Response({
            'conversation_id': conversation.id,
            'user_message': AIMessageSerializer(user_message).data,
            'assistant_message': AIMessageSerializer(assistant_message).data,
            'ai_status': 'completed'
        })


class AIConversationDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        conversation = get_object_or_404(
            AIConversation,
            pk=pk,
            owner=request.user
        )

        conversation.delete()

        return Response(
            {'message': 'Conversation deleted successfully.'},
            status=status.HTTP_200_OK
        )
