from django.db import models
import uuid
from .manager import UserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils import timezone


class User(AbstractBaseUser, PermissionsMixin):
    """Custom User model with UUID primary key and role-based system"""

    ROLE_CHOICES = [
        ('guest', 'Guest'),
        ('host', 'Host'),
        ('admin', 'Admin'),
    ]

    user_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        db_index=True
    )
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    role = models.CharField(max_length=10,
                            choices=ROLE_CHOICES,
                            default='guest')
    created_at = models.DateTimeField(default=timezone.now)

    password = models.CharField(max_length=128)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'  # Use email as the unique identifier
    REQUIRED_FIELDS = ['first_name', 'last_name']  # when creating superuser

    class Meta:
        db_table = 'users'
        indexes = [
            models.Index(fields=['user_id']),
            models.Index(fields=['email']),
            models.Index(fields=['role']),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def is_admin(self):
        return self.role == 'admin'

    def is_host(self):
        return self.role == 'host'

    def is_guest(self):
        return self.role == 'guest'


class Conversation(models.Model):
    """Models for conversations"""
    conversation_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        db_index=True
    )
    participants = models.ManyToManyField(
        User,
        related_name='conversations')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'conversations'
        indexes = [
            models.Index(fields=['conversation_id']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        participant_names = [p.full_name for p in self.participants.all()[:2]]
        return f"Conversation: {', '.join(participant_names)}"


class Message(models.Model):
    message_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        db_index=True
    )
    conversation = models.ForeignKey(  # Fixed: Link to conversation
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_messages'
    )
    message_body = models.TextField(null=False)
    sent_at = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)

    class Meta:
        db_table = 'messages'
        indexes = [
            models.Index(fields=['message_id']),
            models.Index(fields=['conversation', 'sent_at']),
            models.Index(fields=['sender']),
        ]
        ordering = ['-sent_at']

    def __str__(self):
        return f"Message from {self.sender.full_name}: {self.message_body[:50]}"
            
    def mark_as_read(self):
        """Mark message as read"""
        self.is_read = True
        self.save(update_fields=['is_read'])
