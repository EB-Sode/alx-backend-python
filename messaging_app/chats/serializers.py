from rest_framework import serializers
from .models import User, Conversation, Message


# Serializers stated here
class UserSerializer(serializers.ModelSerializer):

    # Read-only property field that combines first_name and last_name
    full_name = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = ['user_id', 'first_name', 'last_name', 'role', 'full_name',
                  'email', 'phone_number', 'created_at', 'password']

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

    # Fields that cannot be modified via API (system-generated)
    read_only_fields = ['user_id', 'created_at']


class UserRegisterSerializer(serializers.ModelSerializer):
    """
    Serializers for registering users with password validation"""
    password = serializers.CharField(write_only=True, min_length=8)
    # Write-only password confirmation field
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        # Only include fields needed for user creation
        fields = ['first_name', 'last_name', 'email', 'full_name',
                  'phone_number', 'role', 'password', 'password_confirm']

    def validate(self, attrs):
        """
        Object-level validation to ensure passwords match
        Called after all field-level validations pass
        """
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs

    def create(self, validated_data):
        """
        Create user with properly hashed password
        Removes password_confirm and uses Django's built-in password hashing
        """
        # Remove password_confirm as it's not needed for user creation
        validated_data.pop('password_confirm')
        # Extract password to hash it separately
        password = validated_data.pop('password')
        # Create user using custom manager method (handles password hashing)
        user = User.objects.create_user(password=password, **validated_data)
        return user


class ConversationMiniSerializer(serializers.ModelSerializer):
    """Mini serializer for Conversation (inside Message)"""
    participants = UserSerializer(many=True, read_only=True)

    class Meta:
        model = Conversation
        fields = ['conversation_id', 'participants', 'created_at']


class MessageSerializer(serializers.ModelSerializer):
    """
    Serializer for Message model with nested sender information
    Provides complete message details including sender info for display
    """
    # Nested serializer to include full sender details in response
    # Uses 'sender_id' field from model but displays as 'sender'
    sender = UserSerializer(source='sender_id', read_only=True)
    conversation = serializers.SerializerMethodField()

    # Write-only field for creating messages (accepts user ID)
    sender = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        write_only=True
    )
    sender_details = UserSerializer(source='sender', read_only=True)

    class Meta:
        model = Message
        fields = [
            'message_id',       # Primary key UUID
            'conversation',     # Foreign key to conversation
            'sender',           # Nested sender details (read-only)
            'sender_id',        # Sender ID for creation (write-only)
            'message_body',     # Message content
            'sent_at',          # Timestamp when message was sent
            'conversation',
            'sender_details'
        ]
        # Fields that are automatically set by system
        read_only_fields = ['message_id', 'sent_at']

    def validate_sender_id(self, value):
        """
        Field-level validation to ensure sender is a conversation participant
        Prevents users from sending messages to conversations they're not part
        of
        """
        # Get conversation ID from the request data
        conversation_id = self.initial_data.get('conversation')
        if conversation_id:
            try:
                # Check if conversation exists and sender is a participant
                conversation = Conversation.objects.get(pk=conversation_id)
                if value not in conversation.participants.all():
                    raise serializers.ValidationError(
                        "Sender must be a participant in the conversation"
                    )
            except Conversation.DoesNotExist:
                raise serializers.ValidationError("Invalid conversation")
        return value


class ConversationSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True, read_only=True)
    created_by = serializers.CharField(source="created_by.first_name",
                                       read_only=True)
    messages = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = [
            'conversation_id', 'participants', 'created_at',
            'messages', 'created_by',
        ]

    def get_messages(self, obj):
        """
        Returns all messages belonging to this conversation
        """
        messages = Message.objects.filter(conversation=obj).order_by("sent_at")
        return MessageSerializer(messages, many=True).data
