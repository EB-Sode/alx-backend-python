# messaging/views.py
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

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
