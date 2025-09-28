from rest_framework import serializers
from .models import Field, FieldImage, FieldAvailability


class FieldImageSerializer(serializers.ModelSerializer):
    """
    Serializer for field images
    """
    class Meta:
        model = FieldImage
        fields = ['id', 'image', 'caption', 'is_primary']


class FieldAvailabilitySerializer(serializers.ModelSerializer):
    """
    Serializer for field availability
    """
    weekday_display = serializers.CharField(source='get_weekday_display', read_only=True)
    
    class Meta:
        model = FieldAvailability
        fields = ['id', 'weekday', 'weekday_display', 'start_time', 'end_time', 'is_available', 'special_price']


class FieldListSerializer(serializers.ModelSerializer):
    """
    Serializer for field list view (basic info)
    """
    primary_image = serializers.SerializerMethodField()
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Field
        fields = [
            'id', 'name', 'type', 'type_display', 'location', 'capacity', 
            'price_per_hour', 'status', 'status_display', 'primary_image',
            'has_lighting', 'has_parking'
        ]

    def get_primary_image(self, obj):
        primary_image = obj.images.filter(is_primary=True).first()
        if primary_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(primary_image.image.url)
        return None


class FieldDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for field detail view (complete info)
    """
    images = FieldImageSerializer(many=True, read_only=True)
    availability_rules = FieldAvailabilitySerializer(many=True, read_only=True)
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Field
        fields = [
            'id', 'name', 'type', 'type_display', 'location', 'address', 'capacity',
            'price_per_hour', 'description', 'status', 'status_display',
            'length', 'width', 'surface_type',
            'has_lighting', 'has_parking', 'has_changing_room', 'has_shower',
            'opening_time', 'closing_time', 'images', 'availability_rules',
            'created_at', 'updated_at'
        ]


class FieldCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating fields
    """
    images = FieldImageSerializer(many=True, read_only=True)
    uploaded_images = serializers.ListField(
        child=serializers.ImageField(max_length=1000000, allow_empty_file=False, use_url=False),
        write_only=True,
        required=False
    )

    class Meta:
        model = Field
        fields = [
            'id', 'name', 'type', 'location', 'address', 'capacity',
            'price_per_hour', 'description', 'status',
            'length', 'width', 'surface_type',
            'has_lighting', 'has_parking', 'has_changing_room', 'has_shower',
            'opening_time', 'closing_time', 'images', 'uploaded_images'
        ]

    def create(self, validated_data):
        uploaded_images = validated_data.pop('uploaded_images', [])
        field = Field.objects.create(**validated_data)
        
        for i, image in enumerate(uploaded_images):
            FieldImage.objects.create(
                field=field,
                image=image,
                is_primary=(i == 0)  # First image is primary
            )
        
        return field

    def update(self, instance, validated_data):
        uploaded_images = validated_data.pop('uploaded_images', [])
        
        # Update field instance
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Add new images if provided
        if uploaded_images:
            for image in uploaded_images:
                FieldImage.objects.create(
                    field=instance,
                    image=image,
                    is_primary=False
                )
        
        return instance