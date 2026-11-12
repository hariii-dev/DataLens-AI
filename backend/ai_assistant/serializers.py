from rest_framework import serializers
from .models import AIConversation, AIMessage


class AIMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIMessage
        fields = ['id', 'role', 'content', 'created_at']
        read_only_fields = fields


class AIConversationSerializer(serializers.ModelSerializer):
    messages = AIMessageSerializer(many=True, read_only=True)

    class Meta:
        model = AIConversation
        fields = [
            'id',
            'dataset',
            'title',
            'messages',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'title',
            'messages',
            'created_at',
            'updated_at',
        ]
