from rest_framework import routers
from django.urls import path, include
from .views import UserViewSet, ConversationViewSet, MessageViewSet

router = routers.DefaultRouter()
router.register(r'users', UserViewSet, basename="user")
router.register(r'conversations', ConversationViewSet, basename="conversation")
router.register(r'messages', MessageViewSet, basename="message")

urlpatterns = [
    path("", include(router.urls)),
]