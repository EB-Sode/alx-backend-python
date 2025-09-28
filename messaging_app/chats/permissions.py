from rest_framework.permissions import SAFE_METHODS
from rest_framework import permissions


class IsParticipantOfConversation(permissions.BasePermission):
    """
    Allow only participants of a conversation to send, view,
    update, and delete messages.
    """

    def has_permission(self, request, view):
        # Must be authenticated for any action
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """
        Object-level check:
        - For Message objects → verify user in conversation participants
        - For Conversation objects → verify user in participants
        """
        if hasattr(obj, "conversation"):  # Message object
            is_participant = obj.conversation.participants.filter(
                id=request.user.id
            ).exists()

        elif hasattr(obj, "participants"):  # Conversation object
            is_participant = obj.participants.filter(
                id=request.user.id).exists()

        else:
            return False

        # Explicitly allow participants full CRUD
        if request.method in SAFE_METHODS:
            return is_participant
        elif request.method in ["POST", "PUT", "PATCH", "DELETE"]:
            return is_participant
        return False
