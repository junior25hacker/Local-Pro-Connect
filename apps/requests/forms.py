from django import forms
from .models import ServiceRequest, PriceRange


class ServiceRequestForm(forms.ModelForm):
    class Meta:
        model = ServiceRequest
        fields = [
            "description",
            "date_time",
            "price_range",
            "urgent",
        ]

        widgets = {
            "description": forms.Textarea(
                attrs={
                    "placeholder": "Describe the problem...",
                    "rows": 4,
                    "class": "input-textarea",
                }
            ),

            "date_time": forms.DateTimeInput(
                attrs={
                    "type": "datetime-local",
                    "class": "input-field",
                }
            ),

            "price_range": forms.Select(
                attrs={
                    "class": "input-select",
                }
            ),

            "urgent": forms.CheckboxInput(
                attrs={
                    "class": "urgent-toggle",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Make optional fields explicit (UI spec compliance)
        self.fields["date_time"].required = False
        self.fields["price_range"].required = False

        # Empty label for optional price
        self.fields["price_range"].queryset = PriceRange.objects.all()
        self.fields["price_range"].empty_label = "Select price range (optional)"