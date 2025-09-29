from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Message

User = get_user_model()


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
    """
    message = get_object_or_404(
        Message.objects.select_related(
            "sender", "receiver").prefetch_related("replies"),
        id=message_id
    )

    data = {
        "id": message.id,
        "sender": str(message.sender),
        "receiver": str(message.receiver),
        "content": message.content,
        "timestamp": message.timestamp,
        "edited": message.edited,
        "replies": message.get_threaded_replies()
    }

    return JsonResponse(data, safe=False)
