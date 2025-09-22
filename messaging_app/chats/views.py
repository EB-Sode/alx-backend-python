from rest_framework import (viewsets, filters, status)
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authentication import (BasicAuthentication,
                                           SessionAuthentication)
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, PermissionDenied
from django.db.models import Prefetch
from .models import User, Conversation, Message
from .serializers import (
    UserSerializer,
    UserRegisterSerializer,
    ConversationSerializer,
    MessageSerializer,
)
from .permissions import IsParticipantOfConversation
from .pagination import MessagePagination


# User Views
class UserViewSet(viewsets.ModelViewSet):
    """
    Handles listing, retrieving, updating, and deleting users
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = [BasicAuthentication, SessionAuthentication]
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        # Use registration serializer only for 'register' action
        if self.action == "register":
            return UserRegisterSerializer
        return UserSerializer

    @action(detail=False, methods=["post"],
            permission_classes=[AllowAny])
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
    authentication_classes = [BasicAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated, IsParticipantOfConversation]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["participants__first_name", "participants__last_name"]
    ordering_fields = ["created_at"]

    def get_queryset(self):
        """
        Restrict conversations to only those the current user participates in,
        and optimize DB queries by prefetching participants and messages.
        """
        return (
            Conversation.objects.filter(participants=self.request.user)
            .prefetch_related(
                "participants",
                Prefetch(
                    "message_set",
                    queryset=Message.objects.select_related("sender")
                )
            )
        )

    def perform_create(self, serializer):
        """
        When creating a conversation:
        - Save the conversation
        - Automatically add the requesting user as a participant
        """
        conversation = serializer.save()
        conversation.participants.add(self.request.user)
        return conversation

    def perform_update(self, serializer):
        """
        Prevent users who are not participants from updating a conversation.
        """
        if not serializer.instance.participants.filter(
                id=self.request.user.id).exists():
            return Response(
                {"detail": "You cannot update this conversation."},
                status=status.HTTP_403_FORBIDDEN
            )
        serializer.save()

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
    authentication_classes = BasicAuthentication, SessionAuthentication
    permission_classes = [IsAuthenticated, IsParticipantOfConversation]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["message_body", "sender__first_name", "sender__last_name"]
    ordering_fields = ["sent_at"]
    pagination_class = MessagePagination

    def get_queryset(self):
        """
        Restrict messages to:
        - The conversation specified in the URL (conversation_pk)
        - AND only if the current user is a participant of that conversation
        """
        conversation_id = self.kwargs.get("conversation_pk")
        user = self.request.user
        return Message.objects.filter(
            conversation_id=conversation_id,
            conversation__participants=user
        )

    def perform_create(self, serializer):
        """
        When creating a message:
        - Fetch the conversation from URL
        - Ensure the user is a participant
        - Save the message with sender + conversation
        """
        conversation_id = self.kwargs.get("conversation_pk")
        conversation = Conversation.objects.filter(
            conversation_id=conversation_id).first()

        if not conversation:
            raise NotFound("Conversation not found.")

        if not conversation.participants.filter(
                id=self.request.user.id).exists():
            raise PermissionDenied(
                "Not allowed to send messages in this conversation.")

        serializer.save(sender=self.request.user, conversation=conversation)
