from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.shortcuts import Http404
from .models import Message
from django.views.decorators.cache import cache_page


@login_required
def delete_user(request):
    """
    Allow the logged-in user to delete their own account.
    """
    user = request.user
    user.delete()
    return JsonResponse({
        "message": "Your account and related data have been deleted."
        })


def get_message_thread(request, message_id):
    """
    View that returns a message with all its threaded replies.
    Ensures that the message belongs to the current user (as sender).
    """
    message = Message.objects.filter(
        id=message_id,
        sender=request.user  # security check
    ).select_related("sender", "receiver").prefetch_related("replies").first()

    if not message:
        raise Http404("Message not found or you don't have access.")

    data = {
        "id": message.id,
        "sender": str(message.sender),
        "receiver": str(message.receiver),
        "content": message.content,
        "timestamp": message.timestamp,
        "edited": message.edited,
        "replies": message.get_threaded_replies()  # recursion in model
    }

    return JsonResponse(data, safe=False)


def unread_messages(request):
    """Return only unread messages for logged-in user"""
    user = request.user
    if not user.is_authenticated:
        return JsonResponse({"error": "Authentication required"}, status=403)

    unread_msgs = Message.unread.for_user(user)

    data = [
        {
            "id": msg.id,
            "sender": str(msg.sender),
            "content": msg.content,
            "timestamp": msg.timestamp,
        }
        for msg in unread_msgs
    ]
    return JsonResponse(data, safe=False)


# Function-based view with caching
@cache_page(60)  # cache this view for 60 seconds
def conversation_messages(request, conversation_id):
    messages = (
        Message.objects.filter(
            parent_message__isnull=True, receiver_id=conversation_id)
        .select_related("sender", "receiver")
        .only("id", "sender__username", "receiver__username",
              "content", "timestamp", "edited", "read")
    )

    data = [
        {
            "id": msg.id,
            "sender": str(msg.sender),
            "receiver": str(msg.receiver),
            "content": msg.content,
            "timestamp": msg.timestamp,
            "edited": msg.edited,
            "read": msg.read,
            "replies": msg.get_threaded_replies(),
        }
        for msg in messages
    ]

    return JsonResponse(data, safe=False)
