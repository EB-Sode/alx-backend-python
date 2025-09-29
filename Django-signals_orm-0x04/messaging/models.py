from django.db import models
from django.conf import settings

# Create your models here.

User = settings.AUTH_USER_MODEL


class Message(models.Model):
    sender = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name="sent_messages")
    receiver = models.ForeignKey(User,
                                 on_delete=models.CASCADE,
                                 related_name="received_messages")
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    edited = models.BooleanField(default=False)

    def __str__(self):
        return f"From {self.sender} to {self.receiver}: {self.content[:30]}"


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

    def __str__(self):
        return f"History of Message {self.message.id} at {self.edited_at}"
