from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import ChatRoom, ChatMessage
from .serializers import (
    ChatRoomListSerializer,
    ChatRoomDetailSerializer,
    ChatRoomCreateSerializer,
    ChatMessageSerializer,
    MessageCreateSerializer
)


class ChatRoomViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing chat rooms
    """
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        
        if user.role == 'admin':
            # Admin can see all chat rooms
            return ChatRoom.objects.all().select_related('user', 'admin', 'field').prefetch_related('messages')
        else:
            # Users can only see their own chat rooms
            return ChatRoom.objects.filter(user=user).select_related('admin', 'field').prefetch_related('messages')

    def get_serializer_class(self):
        if self.action == 'create':
            return ChatRoomCreateSerializer
        elif self.action == 'list':
            return ChatRoomListSerializer
        else:
            return ChatRoomDetailSerializer

    @action(detail=True, methods=['post'])
    def assign_admin(self, request, pk=None):
        """
        Assign an admin to a chat room (admin only)
        """
        if request.user.role != 'admin':
            return Response(
                {'error': 'Only admin can assign chat rooms'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        chat_room = self.get_object()
        admin_id = request.data.get('admin_id')
        
        if not admin_id:
            return Response(
                {'error': 'admin_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            from apps.users.models import User
            admin = User.objects.get(id=admin_id, role='admin')
            
            chat_room.admin = admin
            chat_room.save()
            
            # Create assignment record
            from .models import ChatRoomAssignment
            ChatRoomAssignment.objects.create(
                chat_room=chat_room,
                admin=admin,
                assigned_by=request.user
            )
            
            return Response({'message': 'Admin assigned successfully'})
            
        except User.DoesNotExist:
            return Response(
                {'error': 'Admin not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        """
        Get messages for a chat room with pagination
        """
        chat_room = self.get_object()
        
        # Check access permissions
        user = request.user
        if user.role != 'admin' and chat_room.user != user:
            return Response(
                {'error': 'Access denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Pagination
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 20))
        offset = (page - 1) * page_size
        
        messages = chat_room.messages.all()[offset:offset + page_size]
        serializer = ChatMessageSerializer(messages, many=True)
        
        return Response({
            'messages': serializer.data,
            'has_more': chat_room.messages.count() > offset + page_size
        })

    @action(detail=True, methods=['post'])
    def send_message(self, request, pk=None):
        """
        Send a message to a chat room
        """
        chat_room = self.get_object()
        
        # Check access permissions
        user = request.user
        if user.role != 'admin' and chat_room.user != user:
            return Response(
                {'error': 'Access denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = MessageCreateSerializer(
            data=request.data,
            context={'request': request, 'chat_room_id': chat_room.id}
        )
        
        if serializer.is_valid():
            message = serializer.save()
            return Response(
                ChatMessageSerializer(message).data,
                status=status.HTTP_201_CREATED
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """
        Mark messages as read
        """
        chat_room = self.get_object()
        user = request.user
        
        # Check access permissions
        if user.role != 'admin' and chat_room.user != user:
            return Response(
                {'error': 'Access denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        message_ids = request.data.get('message_ids', [])
        
        if user.role == 'admin':
            ChatMessage.objects.filter(
                id__in=message_ids,
                chat_room=chat_room
            ).update(is_read_by_admin=True)
        else:
            ChatMessage.objects.filter(
                id__in=message_ids,
                chat_room=chat_room
            ).update(is_read_by_user=True)
        
        return Response({'message': 'Messages marked as read'})

    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """
        Get total unread message count for user
        """
        user = request.user
        total_unread = 0
        
        if user.role == 'admin':
            # Count unread messages from users across all rooms assigned to this admin
            chat_rooms = ChatRoom.objects.filter(admin=user)
            for room in chat_rooms:
                total_unread += room.unread_count_for_admin
        else:
            # Count unread messages from admins in user's rooms
            chat_rooms = ChatRoom.objects.filter(user=user)
            for room in chat_rooms:
                total_unread += room.unread_count_for_user
        
        return Response({'unread_count': total_unread})