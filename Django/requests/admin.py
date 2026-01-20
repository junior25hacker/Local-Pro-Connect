from django.contrib import admin
from django.utils import timezone
from .models import ServiceRequest, PriceRange, RequestPhoto, RequestDecisionToken

# Import completion models once migrations are run
try:
    from .completion_models import JobCompletion, ServiceRating, ServiceFeedback
    COMPLETION_MODELS_AVAILABLE = True
except ImportError:
    COMPLETION_MODELS_AVAILABLE = False


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


# Register completion models if available
if COMPLETION_MODELS_AVAILABLE:
    
    class ServiceRatingInline(admin.TabularInline):
        model = ServiceRating
        extra = 0
        can_delete = False
        readonly_fields = ('stars', 'feedback', 'submitted_at', 'rated_by', 'provider')
        fields = ('stars', 'feedback', 'would_recommend', 'would_hire_again', 'is_public', 'submitted_at')
    
    
    @admin.register(JobCompletion)
    class JobCompletionAdmin(admin.ModelAdmin):
        list_display = ('id', 'service_request', 'completed_by', 'work_quality', 'completed_on_time', 'completed_at')
        list_filter = ('work_quality', 'completed_on_time', 'provider_showed_up', 'completed_at')
        search_fields = ('service_request__id', 'completed_by__username', 'completion_notes')
        readonly_fields = ('completed_at', 'created_at', 'updated_at')
        inlines = [ServiceRatingInline]
        
        fieldsets = (
            ('Completion Details', {
                'fields': ('service_request', 'completed_by', 'completed_at')
            }),
            ('Assessment', {
                'fields': ('work_quality', 'completed_on_time', 'provider_showed_up')
            }),
            ('Notes', {
                'fields': ('completion_notes',)
            }),
            ('Timestamps', {
                'fields': ('created_at', 'updated_at'),
                'classes': ('collapse',)
            }),
        )
    
    
    @admin.register(ServiceRating)
    class ServiceRatingAdmin(admin.ModelAdmin):
        list_display = ('id', 'get_request_id', 'stars', 'rated_by', 'provider', 'would_recommend', 'submitted_at')
        list_filter = ('stars', 'would_recommend', 'would_hire_again', 'is_public', 'submitted_at')
        search_fields = ('job_completion__service_request__id', 'rated_by__username', 'provider__username', 'feedback')
        readonly_fields = ('submitted_at', 'job_completion', 'rated_by', 'provider')
        
        fieldsets = (
            ('Rating Information', {
                'fields': ('job_completion', 'stars', 'feedback')
            }),
            ('Detailed Ratings', {
                'fields': ('quality_rating', 'timeliness_rating', 'communication_rating', 'professionalism_rating'),
                'classes': ('collapse',)
            }),
            ('Recommendations', {
                'fields': ('would_recommend', 'would_hire_again', 'is_public')
            }),
            ('Participants', {
                'fields': ('rated_by', 'provider')
            }),
            ('Provider Response', {
                'fields': ('provider_response', 'provider_response_date'),
                'classes': ('collapse',)
            }),
            ('Timestamps', {
                'fields': ('submitted_at',),
                'classes': ('collapse',)
            }),
        )
        
        def get_request_id(self, obj):
            return obj.job_completion.service_request.id
        get_request_id.short_description = 'Request ID'
        get_request_id.admin_order_field = 'job_completion__service_request__id'
    
    
    @admin.register(ServiceFeedback)
    class ServiceFeedbackAdmin(admin.ModelAdmin):
        list_display = ('id', 'service_request', 'feedback_type', 'category', 'priority', 'status', 'submitted_by', 'submitted_at')
        list_filter = ('feedback_type', 'category', 'priority', 'status', 'submitted_at')
        search_fields = ('service_request__id', 'submitted_by__username', 'feedback_text')
        readonly_fields = ('submitted_at', 'updated_at', 'submitted_by', 'service_request')
        
        fieldsets = (
            ('Feedback Information', {
                'fields': ('service_request', 'submitted_by', 'feedback_type', 'category', 'priority')
            }),
            ('Feedback Content', {
                'fields': ('feedback_text',)
            }),
            ('Status & Response', {
                'fields': ('status', 'admin_response', 'admin_response_by', 'admin_response_date')
            }),
            ('Timestamps', {
                'fields': ('submitted_at', 'updated_at'),
                'classes': ('collapse',)
            }),
        )
        
        def save_model(self, request, obj, form, change):
            if change and 'admin_response' in form.changed_data and obj.admin_response:
                obj.admin_response_by = request.user
                obj.admin_response_date = timezone.now()
            super().save_model(request, obj, form, change)