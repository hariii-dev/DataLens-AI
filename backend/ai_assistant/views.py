from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from datasets.models import Dataset
from .models import AIConversation, AIMessage
from .serializers import AIConversationSerializer, AIMessageSerializer
from .services import build_dataset_context, build_ai_prompt


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

        question = request.data.get('question', '').strip()

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

            user_message = AIMessage.objects.create(
                conversation=conversation,
                role='user',
                content=question
            )

            conversation.updated_at = user_message.created_at
            conversation.save(update_fields=['updated_at'])

            return Response({
                'conversation_id': conversation.id,
                'message': AIMessageSerializer(user_message).data,
                'prompt': prompt,
                'ai_status': 'awaiting_provider'
            })

        except Exception as exc:
            return Response(
                {'error': 'Unable to prepare dataset context.'},
                status=status.HTTP_400_BAD_REQUEST
            )
