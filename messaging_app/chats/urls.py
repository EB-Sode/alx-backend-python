from django.urls import path, include
from rest_framework_nested import routers
from .auth import CustomTokenObtainPairView
from .views import UserViewSet, ConversationViewSet, MessageViewSet
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

# Main router
router = routers.DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'conversations', ConversationViewSet, basename='conversation')

# Nested router for messages inside conversations
conversations_router = routers.NestedDefaultRouter(router, r'conversations',
                                                   lookup='conversation')
conversations_router.register(r'messages', MessageViewSet,
                              basename='conversation-messages')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(conversations_router.urls)),
    path("token/", CustomTokenObtainPairView.as_view(),
         name="custom_token_obtain_pair"),
    path("refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
