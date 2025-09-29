from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Message, Notification, MessageHistory

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


User = get_user_model()


class UserDeletionCleanupTests(TestCase):
    def setUp(self):
        # Create two users
        self.user1 = User.objects.create_user(
            username="user1", password="pass123"
        )
        self.user2 = User.objects.create_user(
            username="user2", password="pass123"
        )

        # Create a message from user1 -> user2
        self.message = Message.objects.create(
            sender=self.user1, receiver=self.user2, content="Hello!"
        )

        # Create a notification for user2
        self.notification = Notification.objects.create(
            user=self.user2, message=self.message
        )

        # Create message history (simulate edit)
        self.history = MessageHistory.objects.create(
            message=self.message, old_content="Old text"
        )

    def test_user_deletion_cleans_related_data(self):
        # Delete user1 (sender)
        self.user1.delete()

        # Ensure messages from user1 are deleted
        self.assertEqual(Message.objects.count(), 0)

        # Ensure related message history is deleted
        self.assertEqual(MessageHistory.objects.count(), 0)

        # Notifications should also be deleted (if linked to deleted messages)
        self.assertEqual(Notification.objects.count(), 0)

    def test_receiver_deletion_cleans_related_data(self):
        # Delete user2 (receiver)
        self.user2.delete()

        # Ensure messages to user2 are deleted
        self.assertEqual(Message.objects.count(), 0)

        # Ensure message history cleaned up
        self.assertEqual(MessageHistory.objects.count(), 0)

        # Notifications for user2 should be deleted
        self.assertEqual(Notification.objects.count(), 0)
