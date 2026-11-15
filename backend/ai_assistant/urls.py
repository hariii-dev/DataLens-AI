from django.urls import path
from .views import (
    AIConversationListView,
    AIChatView,
    AIConversationDeleteView,
)

urlpatterns = [
    path('conversations/', AIConversationListView.as_view(), name='ai-conversations'),
    path('conversations/<int:pk>/', AIConversationDeleteView.as_view(), name='ai-conversation-delete'),
    path('conversations/<int:pk>/chat/', AIChatView.as_view(), name='ai-chat'),
]
