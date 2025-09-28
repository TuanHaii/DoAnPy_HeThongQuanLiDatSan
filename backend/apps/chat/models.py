from django.db import models
from apps.users.models import User
from apps.fields.models import Field


class ChatRoom(models.Model):
    """
    Model representing a chat room between user and admin
    """
    ROOM_TYPE_CHOICES = (
        ('general', 'General Support'),
        ('booking', 'Booking Support'),
        ('field_inquiry', 'Field Inquiry'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_rooms')
    admin = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='admin_chat_rooms',
        limit_choices_to={'role': 'admin'}
    )
    field = models.ForeignKey(
        Field, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        help_text="Related field for field inquiries"
    )
    room_type = models.CharField(max_length=20, choices=ROOM_TYPE_CHOICES, default='general')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_message_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        admin_name = self.admin.full_name if self.admin else "Unassigned"
        return f"Chat: {self.user.username} <-> {admin_name}"

    @property
    def unread_count_for_user(self):
        """Count unread messages for the user"""
        return self.messages.filter(sender__role='admin', is_read_by_user=False).count()

    @property
    def unread_count_for_admin(self):
        """Count unread messages for the admin"""
        return self.messages.filter(sender__role='user', is_read_by_admin=False).count()

    class Meta:
        db_table = 'chat_rooms'
        ordering = ['-last_message_at']


class ChatMessage(models.Model):
    """
    Model representing a chat message
    """
    MESSAGE_TYPE_CHOICES = (
        ('text', 'Text'),
        ('image', 'Image'),
        ('file', 'File'),
        ('system', 'System Message'),
    )

    chat_room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPE_CHOICES, default='text')
    content = models.TextField()
    file_url = models.URLField(blank=True, null=True, help_text="URL for images or files")
    
    # Read status
    is_read_by_user = models.BooleanField(default=False)
    is_read_by_admin = models.BooleanField(default=False)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Auto-mark as read by sender
        if self.sender.role == 'user':
            self.is_read_by_user = True
        elif self.sender.role == 'admin':
            self.is_read_by_admin = True
        
        super().save(*args, **kwargs)
        
        # Update chat room's last message time
        self.chat_room.last_message_at = self.created_at
        self.chat_room.save(update_fields=['last_message_at'])

    def __str__(self):
        return f"{self.sender.username}: {self.content[:50]}..."

    class Meta:
        db_table = 'chat_messages'
        ordering = ['created_at']


class ChatRoomAssignment(models.Model):
    """
    Model for tracking admin assignments to chat rooms
    """
    chat_room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='assignments')
    admin = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'admin'})
    assigned_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='admin_assignments'
    )
    assigned_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.admin.full_name} assigned to {self.chat_room}"

    class Meta:
        db_table = 'chat_room_assignments'
        ordering = ['-assigned_at']