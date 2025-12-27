from django.contrib import admin
from .models import ServiceRequest, PriceRange, RequestPhoto


class RequestPhotoInline(admin.TabularInline):
    model = RequestPhoto
    extra = 1


@admin.register(ServiceRequest)
class ServiceRequestAdmin(admin.ModelAdmin):
    list_display = ("id", "urgent", "price_range", "created_at")
    list_filter = ("urgent", "price_range")
    search_fields = ("description",)
    inlines = [RequestPhotoInline]


@admin.register(PriceRange)
class PriceRangeAdmin(admin.ModelAdmin):
    list_display = ("label", "min_price", "max_price")