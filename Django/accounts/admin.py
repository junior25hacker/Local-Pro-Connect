from django.contrib import admin
from .models import UserProfile, ProviderProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'city', 'state', 'created_at')
    list_filter = ('city', 'state', 'created_at')
    search_fields = ('user__username', 'user__email', 'phone', 'city')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Contact Information', {
            'fields': ('phone', 'address')
        }),
        ('Location', {
            'fields': ('city', 'state', 'zip_code')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ProviderProfile)
class ProviderProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'company_name', 'service_type', 'phone', 'is_verified', 'rating', 'created_at')
    list_filter = ('service_type', 'is_verified', 'created_at', 'rating')
    search_fields = ('user__username', 'user__email', 'company_name', 'phone', 'city')
    readonly_fields = ('created_at', 'updated_at', 'services_rendered', 'total_reviews')
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Company Information', {
            'fields': ('company_name', 'service_type', 'service_description')
        }),
        ('Contact Information', {
            'fields': ('phone', 'business_address', 'city', 'state', 'zip_code')
        }),
        ('Profile', {
            'fields': ('bio', 'profile_picture', 'years_experience')
        }),
        ('Service Statistics', {
            'fields': ('services_rendered', 'rating', 'total_reviews', 'is_verified'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
