from django.db import models


class UnreadMessagesManager(models.Manager):
    """Manager to fetch unread messages for a specific user."""
    def for_user(self, user):
        return (
            self.get_queryset()
            .filter(receiver=user, read=False)
            .select_related("sender")  # avoid extra queries
            .only("id", "sender", "content", "timestamp")  # optimize
        )
