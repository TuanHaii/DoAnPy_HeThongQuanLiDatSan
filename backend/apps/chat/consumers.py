import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from .models import ChatRoom, ChatMessage
from apps.users.models import User


class ChatConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time chat
    """
    
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'
        self.user = self.scope["user"]

        # Check if user is authenticated
        if isinstance(self.user, AnonymousUser):
            await self.close()
            return

        # Check if user has access to this chat room
        has_access = await self.check_room_access()
        if not has_access:
            await self.close()
            return

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        # Send user connection status to group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_status',
                'user_id': self.user.id,
                'username': self.user.username,
                'status': 'online'
            }
        )

    async def disconnect(self, close_code):
        # Send user disconnection status to group
        if hasattr(self, 'room_group_name') and hasattr(self, 'user'):
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_status',
                    'user_id': self.user.id,
                    'username': self.user.username,
                    'status': 'offline'
                }
            )

            # Leave room group
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        """
        Receive message from WebSocket
        """
        try:
            text_data_json = json.loads(text_data)
            message_type = text_data_json.get('type', 'chat_message')

            if message_type == 'chat_message':
                await self.handle_chat_message(text_data_json)
            elif message_type == 'mark_read':
                await self.handle_mark_read(text_data_json)
            elif message_type == 'typing':
                await self.handle_typing(text_data_json)

        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'error': 'Invalid JSON'
            }))

    async def handle_chat_message(self, data):
        """
        Handle chat message
        """
        content = data.get('content', '')
        file_url = data.get('file_url', '')
        msg_type = data.get('message_type', 'text')

        if not content.strip() and not file_url:
            return

        # Save message to database
        message = await self.save_message(content, file_url, msg_type)

        if message:
            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': {
                        'id': message.id,
                        'content': message.content,
                        'file_url': message.file_url,
                        'message_type': message.message_type,
                        'sender': {
                            'id': message.sender.id,
                            'username': message.sender.username,
                            'full_name': message.sender.full_name,
                            'role': message.sender.role
                        },
                        'created_at': message.created_at.isoformat(),
                        'is_read_by_user': message.is_read_by_user,
                        'is_read_by_admin': message.is_read_by_admin
                    }
                }
            )

    async def handle_mark_read(self, data):
        """
        Handle mark messages as read
        """
        message_ids = data.get('message_ids', [])
        await self.mark_messages_read(message_ids)

        # Notify group about read status update
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'messages_read',
                'message_ids': message_ids,
                'reader_id': self.user.id,
                'reader_role': self.user.role
            }
        )

    async def handle_typing(self, data):
        """
        Handle typing indicator
        """
        is_typing = data.get('is_typing', False)
        
        # Send typing status to room group (excluding sender)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'typing_status',
                'user_id': self.user.id,
                'username': self.user.username,
                'is_typing': is_typing
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        """
        Send chat message to WebSocket
        """
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event['message']
        }))

    async def user_status(self, event):
        """
        Send user status to WebSocket
        """
        await self.send(text_data=json.dumps({
            'type': 'user_status',
            'user_id': event['user_id'],
            'username': event['username'],
            'status': event['status']
        }))

    async def messages_read(self, event):
        """
        Send read status update to WebSocket
        """
        await self.send(text_data=json.dumps({
            'type': 'messages_read',
            'message_ids': event['message_ids'],
            'reader_id': event['reader_id'],
            'reader_role': event['reader_role']
        }))

    async def typing_status(self, event):
        """
        Send typing status to WebSocket (exclude sender)
        """
        if event['user_id'] != self.user.id:
            await self.send(text_data=json.dumps({
                'type': 'typing_status',
                'user_id': event['user_id'],
                'username': event['username'],
                'is_typing': event['is_typing']
            }))

    @database_sync_to_async
    def check_room_access(self):
        """
        Check if user has access to the chat room
        """
        try:
            chat_room = ChatRoom.objects.get(id=self.room_id)
            
            # User can access if they are the room owner or an admin
            if self.user.role == 'admin':
                return True
            elif chat_room.user == self.user:
                return True
            else:
                return False
        except ChatRoom.DoesNotExist:
            return False

    @database_sync_to_async
    def save_message(self, content, file_url, message_type):
        """
        Save message to database
        """
        try:
            chat_room = ChatRoom.objects.get(id=self.room_id)
            message = ChatMessage.objects.create(
                chat_room=chat_room,
                sender=self.user,
                content=content,
                file_url=file_url,
                message_type=message_type
            )
            return message
        except ChatRoom.DoesNotExist:
            return None

    @database_sync_to_async
    def mark_messages_read(self, message_ids):
        """
        Mark messages as read
        """
        if self.user.role == 'admin':
            ChatMessage.objects.filter(
                id__in=message_ids,
                chat_room_id=self.room_id
            ).update(is_read_by_admin=True)
        else:
            ChatMessage.objects.filter(
                id__in=message_ids,
                chat_room_id=self.room_id
            ).update(is_read_by_user=True)