# chats/permissions.py
from rest_framework import permissions


class IsConversationParticipant(permissions.BasePermission):
    """Only participants can view a conversation and its messages"""

    def has_object_permission(self, request, view, obj):
        return request.user in obj.participants.all()
