from django.db import models
import uuid
from .manager import UserManager
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.utils import timezone

# Create your models here.
#     user_id (Primary Key, UUID, Indexed)
#     first_name (VARCHAR, NOT NULL)
#     last_name (VARCHAR, NOT NULL)
#     email (VARCHAR, UNIQUE, NOT NULL)
#     password_hash (VARCHAR, NOT NULL)
#     phone_number (VARCHAR, NULL)
#     role (ENUM: 'guest', 'host', 'admin', NOT NULL)
#     created_at (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP)
# Message

#     message_id (Primary Key, UUID, Indexed)
#     sender_id (Foreign Key, references User(user_id))
#     message_body (TEXT, NOT NULL)
#     sent_at (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP)
# Conversation

# conversation_id (Primary Key, UUID, Indexed)
# participants_id (Foreign Key, references User(user_id)
# created_at (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP)


class CustomUser(AbstractUser, PermissionsMixin):
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
    first_name = models.CharField(max_length=200, null=False)
    last_name = models.CharField(max_length=200, null=False)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, null=True)
    role = models.CharField(max_length=10,
                            choices=ROLE_CHOICES,
                            default='guest')
    created_at = models.DateTimeField(default=timezone.now)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager

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


class Message(models.Model):
    message_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        db_index=True
    )
    sender_id = models.ForeignKey(CustomUser, on_delete=models.CASCADE,
                                  related_name='messages')
    message_body = models.TextField(null=False)
    sent_at = models.DateTimeField(default=timezone.now)


class Conversation(models.Model):
    conversation_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        db_index=True
    )
    participants = models.ManyToManyField(
        CustomUser,
        on_delete=models.CASCASE,
        related_name='conversation')
    created_at = models.DateTimeField(default=timezone.now)
