from django.db import models
from django.core.validators import MinValueValidator


class Field(models.Model):
    """
    Model representing a sports field
    """
    TYPE_CHOICES = (
        ('soccer', 'Soccer'),
        ('volleyball', 'Volleyball'),
        ('tennis', 'Tennis'),
        ('basketball', 'Basketball'),
        ('badminton', 'Badminton'),
    )
    
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('maintenance', 'Under Maintenance'),
    )

    name = models.CharField(max_length=255)
    type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    location = models.CharField(max_length=255)
    address = models.TextField(blank=True)
    capacity = models.IntegerField(validators=[MinValueValidator(1)])
    price_per_hour = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Field specifications
    length = models.FloatField(null=True, blank=True, help_text="Length in meters")
    width = models.FloatField(null=True, blank=True, help_text="Width in meters")
    surface_type = models.CharField(max_length=100, blank=True, help_text="e.g., Grass, Artificial turf, Wood")
    
    # Facilities
    has_lighting = models.BooleanField(default=False)
    has_parking = models.BooleanField(default=False)
    has_changing_room = models.BooleanField(default=False)
    has_shower = models.BooleanField(default=False)
    
    # Operating hours
    opening_time = models.TimeField(default='06:00')
    closing_time = models.TimeField(default='22:00')
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.type}) - {self.location}"

    class Meta:
        db_table = 'fields'
        ordering = ['name']


class FieldImage(models.Model):
    """
    Model for storing multiple images of a field
    """
    field = models.ForeignKey(Field, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='field_images/')
    caption = models.CharField(max_length=255, blank=True)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.field.name}"

    class Meta:
        db_table = 'field_images'


class FieldAvailability(models.Model):
    """
    Model for defining field availability rules
    """
    WEEKDAY_CHOICES = (
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    )

    field = models.ForeignKey(Field, related_name='availability_rules', on_delete=models.CASCADE)
    weekday = models.IntegerField(choices=WEEKDAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_available = models.BooleanField(default=True)
    special_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"{self.field.name} - {self.get_weekday_display()} {self.start_time}-{self.end_time}"

    class Meta:
        db_table = 'field_availability'
        unique_together = ['field', 'weekday', 'start_time', 'end_time']