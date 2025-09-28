from rest_framework import serializers
from .models import ChatRoom, ChatMessage, ChatRoomAssignment
from apps.users.serializers import UserProfileSerializer
from apps.fields.serializers import FieldListSerializer


class ChatMessageSerializer(serializers.ModelSerializer):
    """
    Serializer for chat messages
    """
    sender = UserProfileSerializer(read_only=True)
    message_type_display = serializers.CharField(source='get_message_type_display', read_only=True)

    class Meta:
        model = ChatMessage
        fields = [
            'id', 'sender', 'content', 'message_type', 'message_type_display',
            'file_url', 'is_read_by_user', 'is_read_by_admin', 'created_at'
        ]


class ChatRoomListSerializer(serializers.ModelSerializer):
    """
    Serializer for chat room list
    """
    user = UserProfileSerializer(read_only=True)
    admin = UserProfileSerializer(read_only=True)
    field = FieldListSerializer(read_only=True)
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    room_type_display = serializers.CharField(source='get_room_type_display', read_only=True)

    class Meta:
        model = ChatRoom
        fields = [
            'id', 'user', 'admin', 'field', 'room_type', 'room_type_display',
            'is_active', 'last_message', 'unread_count', 'created_at', 'last_message_at'
        ]

    def get_last_message(self, obj):
        last_message = obj.messages.last()
        if last_message:
            return {
                'content': last_message.content,
                'sender': last_message.sender.username,
                'created_at': last_message.created_at
            }
        return None

    def get_unread_count(self, obj):
        request = self.context.get('request')
        if request and request.user:
            if request.user.role == 'admin':
                return obj.unread_count_for_admin
            else:
                return obj.unread_count_for_user
        return 0


class ChatRoomDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for chat room detail
    """
    user = UserProfileSerializer(read_only=True)
    admin = UserProfileSerializer(read_only=True)
    field = FieldListSerializer(read_only=True)
    messages = serializers.SerializerMethodField()
    room_type_display = serializers.CharField(source='get_room_type_display', read_only=True)

    class Meta:
        model = ChatRoom
        fields = [
            'id', 'user', 'admin', 'field', 'room_type', 'room_type_display',
            'is_active', 'messages', 'created_at', 'last_message_at'
        ]

    def get_messages(self, obj):
        # Get latest 50 messages
        messages = obj.messages.all()[:50]
        return ChatMessageSerializer(messages, many=True).data


class ChatRoomCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating chat rooms
    """
    class Meta:
        model = ChatRoom
        fields = ['field', 'room_type']

    def create(self, validated_data):
        user = self.context['request'].user
        
        # Check if a room already exists for this user and field (if specified)
        field = validated_data.get('field')
        room_type = validated_data.get('room_type', 'general')
        
        existing_room = None
        if field:
            existing_room = ChatRoom.objects.filter(
                user=user,
                field=field,
                is_active=True
            ).first()
        else:
            existing_room = ChatRoom.objects.filter(
                user=user,
                room_type=room_type,
                field__isnull=True,
                is_active=True
            ).first()
        
        if existing_room:
            return existing_room
        
        # Create new room
        validated_data['user'] = user
        return super().create(validated_data)


class MessageCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating messages
    """
    class Meta:
        model = ChatMessage
        fields = ['content', 'message_type', 'file_url']

    def create(self, validated_data):
        chat_room_id = self.context['chat_room_id']
        user = self.context['request'].user
        
        validated_data['chat_room_id'] = chat_room_id
        validated_data['sender'] = user
        
        return super().create(validated_data)