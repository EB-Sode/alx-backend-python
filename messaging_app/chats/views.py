from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import User, Conversation, Message
from .serializers import (
    UserSerializer,
    UserRegisterSerializer,
    ConversationSerializer,
    MessageSerializer,
)


# User Views
class UserViewSet(viewsets.ModelViewSet):
    """
    Handles listing, retrieving, updating, and deleting users
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    def get_serializer_class(self):
        # Use registration serializer only for 'register' action
        if self.action == "register":
            return UserRegisterSerializer
        return UserSerializer

    @action(detail=False, methods=["post"],
            permission_classes=[permissions.AllowAny])
    def register(self, request, *args, **kwargs):
        """
        Custom endpoint for user registration
        POST /users/register/
        """
        serializer = UserRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(UserSerializer(user).data)


# Conversation Views
class ConversationViewSet(viewsets.ModelViewSet):
    """
    Handles conversation CRUD
    """
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # Add the request user as a participant automatically
        conversation = serializer.save()
        conversation.participants.add(self.request.user)
        return conversation


# Message Views
class MessageViewSet(viewsets.ModelViewSet):
    """
    Handles sending and retrieving messages
    """
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # Ensure sender is the logged-in user
        serializer.save(sender=self.request.user)
