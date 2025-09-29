from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Message, Notification

User = get_user_model()

# Create your tests here.


class MessagingTests(TestCase):
    def setUp(self):
        """Create two users for messaging tests"""
        self.sender = User.objects.create_user(
            username="alice", password="password123"
        )
        self.receiver = User.objects.create_user(
            username="bob", password="password123"
        )

    def test_message_creation_creates_notification(self):
        """Sending a message should automatically create a notification"""
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Hello Bob!"
        )

        # Ensure the message is stored
        self.assertEqual(Message.objects.count(), 1)

        # Ensure a notification was created
        self.assertEqual(Notification.objects.count(), 1)

        notification = Notification.objects.first()
        self.assertEqual(notification.user, self.receiver)
        self.assertEqual(notification.message, message)
        self.assertFalse(notification.is_read)  # default should be False

    def test_multiple_messages_create_multiple_notifications(self):
        """Each new message should create a separate notification"""
        Message.objects.create(sender=self.sender,
                               receiver=self.receiver,
                               content="Hi again!")
        Message.objects.create(sender=self.sender,
                               receiver=self.receiver,
                               content="And again!")

        self.assertEqual(Message.objects.count(), 2)
        self.assertEqual(Notification.objects.count(), 2)

    def test_notification_str(self):
        """String representation should be user-friendly"""
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Test notification"
        )
        notification = Notification.objects.get(message=message)
        self.assertIn("Notification", str(notification))
        self.assertIn(self.receiver.username, str(notification))
