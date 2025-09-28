from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from .models import Field, FieldImage, FieldAvailability
from .serializers import (
    FieldListSerializer,
    FieldDetailSerializer, 
    FieldCreateUpdateSerializer,
    FieldImageSerializer,
    FieldAvailabilitySerializer
)
from .permissions import IsAdminOrReadOnly


class FieldViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing fields
    """
    queryset = Field.objects.all()
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['type', 'status', 'has_lighting', 'has_parking']
    search_fields = ['name', 'location', 'description']
    ordering_fields = ['name', 'price_per_hour', 'capacity', 'created_at']
    ordering = ['name']

    def get_serializer_class(self):
        if self.action == 'list':
            return FieldListSerializer
        elif self.action == 'retrieve':
            return FieldDetailSerializer
        else:
            return FieldCreateUpdateSerializer

    def get_queryset(self):
        queryset = Field.objects.all()
        
        # Filter by price range
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        
        if min_price:
            queryset = queryset.filter(price_per_hour__gte=min_price)
        if max_price:
            queryset = queryset.filter(price_per_hour__lte=max_price)
            
        # Filter by capacity
        min_capacity = self.request.query_params.get('min_capacity')
        if min_capacity:
            queryset = queryset.filter(capacity__gte=min_capacity)
            
        # Show only active fields for non-admin users
        if not (self.request.user.is_authenticated and self.request.user.role == 'admin'):
            queryset = queryset.filter(status='active')
            
        return queryset.prefetch_related('images', 'availability_rules')

    @action(detail=True, methods=['get'])
    def availability(self, request, pk=None):
        """
        Get field availability for a specific date or date range
        """
        field = self.get_object()
        date = request.query_params.get('date')
        
        if date:
            # Return availability for specific date
            # This would typically check against bookings
            return Response({
                'field_id': field.id,
                'date': date,
                'availability': []  # Would be populated with actual availability logic
            })
        
        # Return general availability rules
        availability_rules = field.availability_rules.all()
        serializer = FieldAvailabilitySerializer(availability_rules, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def upload_images(self, request, pk=None):
        """
        Upload images for a field
        """
        field = self.get_object()
        images = request.FILES.getlist('images')
        
        if not images:
            return Response({'error': 'No images provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        created_images = []
        for image in images:
            field_image = FieldImage.objects.create(
                field=field,
                image=image,
                caption=request.data.get('caption', '')
            )
            created_images.append(field_image)
        
        serializer = FieldImageSerializer(created_images, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'])
    def types(self, request):
        """
        Get available field types
        """
        types = [{'value': choice[0], 'label': choice[1]} for choice in Field.TYPE_CHOICES]
        return Response(types)

    @action(detail=False, methods=['get'])
    def popular(self, request):
        """
        Get popular fields (most booked)
        """
        # This would typically be based on booking statistics
        popular_fields = Field.objects.filter(status='active')[:6]
        serializer = FieldListSerializer(popular_fields, many=True, context={'request': request})
        return Response(serializer.data)