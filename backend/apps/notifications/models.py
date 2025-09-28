from django.db import models
from apps.users.models import User


class Notification(models.Model):
    """
    Model representing notifications for users
    """
    TYPE_CHOICES = (
        ('booking_confirmed', 'Booking Confirmed'),
        ('booking_canceled', 'Booking Canceled'),
        ('booking_reminder', 'Booking Reminder'),
        ('chat_message', 'New Chat Message'),
        ('system', 'System Notification'),
        ('promotion', 'Promotion'),
    )

    PRIORITY_CHOICES = (
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    title = models.CharField(max_length=255)
    message = models.TextField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='normal')
    
    # Links and metadata
    related_object_id = models.PositiveIntegerField(null=True, blank=True)
    related_object_type = models.CharField(max_length=50, blank=True)  # 'booking', 'chat_room', etc.
    action_url = models.URLField(blank=True)
    
    # Status
    is_read = models.BooleanField(default=False)
    is_sent = models.BooleanField(default=False)
    
    # Delivery channels
    send_email = models.BooleanField(default=False)
    send_sms = models.BooleanField(default=False)
    send_push = models.BooleanField(default=True)
    
    # Timestamps
    scheduled_at = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.user.username}"

    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['type', 'is_sent']),
            models.Index(fields=['scheduled_at']),
        ]


class NotificationTemplate(models.Model):
    """
    Model for notification templates
    """
    TYPE_CHOICES = Notification.TYPE_CHOICES

    type = models.CharField(max_length=20, choices=TYPE_CHOICES, unique=True)
    title_template = models.CharField(max_length=255)
    message_template = models.TextField()
    email_subject_template = models.CharField(max_length=255, blank=True)
    email_body_template = models.TextField(blank=True)
    sms_template = models.CharField(max_length=160, blank=True)
    
    # Default settings
    default_priority = models.CharField(max_length=10, choices=Notification.PRIORITY_CHOICES, default='normal')
    default_send_email = models.BooleanField(default=False)
    default_send_sms = models.BooleanField(default=False)
    default_send_push = models.BooleanField(default=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Template: {self.get_type_display()}"

    class Meta:
        db_table = 'notification_templates'


class NotificationPreference(models.Model):
    """
    Model for user notification preferences
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_preferences')
    
    # Email preferences
    email_booking_updates = models.BooleanField(default=True)
    email_chat_messages = models.BooleanField(default=False)
    email_promotions = models.BooleanField(default=True)
    email_system_notifications = models.BooleanField(default=True)
    
    # SMS preferences
    sms_booking_updates = models.BooleanField(default=False)
    sms_urgent_notifications = models.BooleanField(default=True)
    
    # Push notification preferences
    push_booking_updates = models.BooleanField(default=True)
    push_chat_messages = models.BooleanField(default=True)
    push_promotions = models.BooleanField(default=False)
    push_system_notifications = models.BooleanField(default=True)
    
    # General settings
    quiet_hours_start = models.TimeField(default='22:00')
    quiet_hours_end = models.TimeField(default='08:00')
    timezone = models.CharField(max_length=50, default='Asia/Ho_Chi_Minh')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Preferences for {self.user.username}"

    class Meta:
        db_table = 'notification_preferences'