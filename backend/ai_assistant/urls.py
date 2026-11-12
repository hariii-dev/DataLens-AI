from django.urls import path
from .views import AIConversationListView, AIChatView

urlpatterns = [
    path('conversations/', AIConversationListView.as_view(), name='ai-conversations'),
    path('conversations/<int:pk>/chat/', AIChatView.as_view(), name='ai-chat'),
]
