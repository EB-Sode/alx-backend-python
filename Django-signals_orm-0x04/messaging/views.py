from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import Http404
from .models import Message


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
