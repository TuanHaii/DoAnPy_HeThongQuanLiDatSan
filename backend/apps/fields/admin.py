from django.contrib import admin
from .models import Field, FieldImage, FieldAvailability


class FieldImageInline(admin.TabularInline):
    model = FieldImage
    extra = 1


class FieldAvailabilityInline(admin.TabularInline):
    model = FieldAvailability
    extra = 1


@admin.register(Field)
class FieldAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'location', 'price_per_hour', 'capacity', 'status', 'created_at')
    list_filter = ('type', 'status', 'has_lighting', 'has_parking', 'created_at')
    search_fields = ('name', 'location', 'description')
    ordering = ('name',)
    inlines = [FieldImageInline, FieldAvailabilityInline]
    
    fieldsets = (
        (None, {
            'fields': ('name', 'type', 'location', 'address', 'status')
        }),
        ('Specifications', {
            'fields': ('capacity', 'length', 'width', 'surface_type', 'description')
        }),
        ('Pricing', {
            'fields': ('price_per_hour',)
        }),
        ('Operating Hours', {
            'fields': ('opening_time', 'closing_time')
        }),
        ('Facilities', {
            'fields': ('has_lighting', 'has_parking', 'has_changing_room', 'has_shower')
        }),
    )


@admin.register(FieldImage)
class FieldImageAdmin(admin.ModelAdmin):
    list_display = ('field', 'caption', 'is_primary', 'created_at')
    list_filter = ('is_primary', 'created_at')
    search_fields = ('field__name', 'caption')