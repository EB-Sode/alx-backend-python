# chats/permissions.py
from rest_framework.permissions import BasePermission


class IsConversationParticipant(BasePermission):
    """Only participants can view a conversation and its messages"""

    def has_object_permission(self, request, view, obj):
        return request.user in obj.participants.all()
