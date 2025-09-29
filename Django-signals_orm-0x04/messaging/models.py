from django.db import models
from django.conf import settings
from .managers import UnreadMessagesManager

# Create your models here.

User = settings.AUTH_USER_MODEL


class Message(models.Model):
    sender = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name="sent_messages")
    receiver = models.ForeignKey(User,
                                 on_delete=models.CASCADE,
                                 related_name="received_messages")
    parent_message = models.ForeignKey("self",
                                       null=True,
                                       blank=True,
                                       related_name="replies",
                                       on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    edited = models.BooleanField(default=False)
    read = models.BooleanField(default=False)  # NEW FIELD

    # Managers
    objects = models.Manager()  # default manager
    unread = UnreadMessagesManager()  # custom manager

    def __str__(self):
        return f"From {self.sender} to {self.receiver}: {self.content[:30]}"

    def get_threaded_replies(self):
        """
        Recursive method to fetch all replies in a threaded format.
        """
        replies = self.replies.select_related("sender", "receiver"
                                              ).prefetch_related("replies")
        result = []
        for reply in replies:
            result.append({
                "id": reply.id,
                "sender": str(reply.sender),
                "receiver": str(reply.receiver),
                "content": reply.content,
                "timestamp": reply.timestamp,
                "edited": reply.edited,
                "replies": reply.get_threaded_replies()  # recursion
            })
        return result


class Notification(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name="notifications")
    message = models.ForeignKey(Message,
                                on_delete=models.CASCADE,
                                related_name="notifications")
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for {self.user} - Message {self.message.id}"


class MessageHistory(models.Model):
    message = models.ForeignKey(Message,
                                on_delete=models.CASCADE,
                                related_name="history")
    old_content = models.TextField()
    edited_at = models.DateTimeField(auto_now_add=True)
    edited_by = models.ForeignKey(User,
                                  on_delete=models.SET_NULL,
                                  null=True,
                                  blank=True)

    def __str__(self):
        return f"History of Message {self.message.id} at {self.edited_at}"
