from django.contrib import admin
from .models import ServiceRequest, PriceRange, RequestPhoto, RequestDecisionToken


class RequestPhotoInline(admin.TabularInline):
    model = RequestPhoto
    extra = 1


class RequestDecisionTokenInline(admin.TabularInline):
    model = RequestDecisionToken
    extra = 0
    can_delete = False
    readonly_fields = ('token', 'created_at', 'expires_at', 'used_at')
    fields = ('token', 'created_at', 'expires_at', 'used', 'used_at')


@admin.register(ServiceRequest)
class ServiceRequestAdmin(admin.ModelAdmin):
    list_display = ("id", "provider_name", "user", "status", "urgent", "created_at")
    list_filter = ("status", "urgent", "price_range", "created_at")
    search_fields = ("description", "provider_name", "user__username")
    readonly_fields = ("created_at", "accepted_at", "declined_at")
    inlines = [RequestPhotoInline, RequestDecisionTokenInline]
    
    fieldsets = (
        ('Request Information', {
            'fields': ('user', 'provider_name', 'description')
        }),
        ('Request Details', {
            'fields': ('date_time', 'price_range', 'urgent')
        }),
        ('Status & Assignment', {
            'fields': ('status', 'provider')
        }),
        ('Decline Information', {
            'fields': ('decline_reason', 'decline_message'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'accepted_at', 'declined_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(PriceRange)
class PriceRangeAdmin(admin.ModelAdmin):
    list_display = ("label", "min_price", "max_price")


@admin.register(RequestDecisionToken)
class RequestDecisionTokenAdmin(admin.ModelAdmin):
    list_display = ("id", "service_request", "created_at", "expires_at", "used", "is_valid")
    list_filter = ("used", "created_at")
    search_fields = ("token", "service_request__id")
    readonly_fields = ("token", "created_at", "expires_at", "used_at")
    
    def is_valid(self, obj):
        return obj.is_valid()
    is_valid.boolean = True
    is_valid.short_description = "Valid"