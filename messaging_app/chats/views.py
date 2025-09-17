from rest_framework import (
    viewsets, permissions,
    filters, status)
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Prefetch
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
        """Registers new users"""
        serializer = UserRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            UserSerializer(user).data, status=status.HTTP_201_CREATED
            )


# Conversation Views
class ConversationViewSet(viewsets.ModelViewSet):
    """
    Handles conversation CRUD
    """
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["participants__first_name", "participants__last_name"]
    ordering_fields = ["created_at"]

    def get_queryset(self):
        return (
            Conversation.objects.filter(participants=self.request.user)
            .prefetch_related(
                "participants",
                Prefetch("message_set",
                         queryset=Message.objects.select_related("sender"))
            )
        )

    def perform_create(self, serializer):
        # Add the request user as a participant automatically
        conversation = serializer.save()
        conversation.participants.add(self.request.user)
        return conversation

    def destroy(self, request, *args, **kwargs):
        """
        Override to return a clear response with status
        """
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {"detail": "Conversation deleted successfully."},
            status=status.HTTP_204_NO_CONTENT
        )


# Message Views
class MessageViewSet(viewsets.ModelViewSet):
    """
    Handles sending and retrieving messages
    """
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["message_body", "sender__first_name", "sender__last_name"]
    ordering_fields = ["sent_at"]

    def get_queryset(self):
        conversation_id = self.kwargs.get("conversation_pk")
        return Message.objects.filter(conversation_id=conversation_id)

    def perform_create(self, serializer):
        conversation_id = self.kwargs.get("conversation_pk")
        conversation = get_object_or_404(Conversation, pk=conversation_id)
        serializer.save(conversation=conversation)
