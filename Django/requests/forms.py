from django import forms
from .models import ServiceRequest, PriceRange
from accounts.models import ProviderProfile


class ServiceRequestForm(forms.ModelForm):
    """
    Request form with provider selection options:
    - provider_choice: preferred dropdown of providers (from ProviderProfile)
    - provider_name: fallback free-text if provider is not listed
    """
    provider_choice = forms.ModelChoiceField(
        queryset=ProviderProfile.objects.select_related("user").all(),
        required=False,
        empty_label="Select a provider (recommended)",
        widget=forms.Select(attrs={"class": "input-select"}),
        help_text="Choose a provider from the list, or enter a name below if not listed.",
        label="Select Provider",
    )

    provider_name = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Enter provider name (fallback)...",
                "class": "input-field",
            }
        ),
        help_text="If you cannot find the provider in the list, enter their name here.",
        label="Provider Name (fallback)",
    )

    class Meta:
        model = ServiceRequest
        fields = [
            "provider_choice",
            "provider_name",
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
        # Optional fields
        self.fields["date_time"].required = False
        self.fields["price_range"].required = False
        # Populate price ranges
        self.fields["price_range"].queryset = PriceRange.objects.all()
        if hasattr(self.fields["price_range"], "empty_label"):
            self.fields["price_range"].empty_label = "Select price range (optional)"

    def clean(self):
        cleaned = super().clean()
        provider_choice = cleaned.get("provider_choice")
        provider_name = (cleaned.get("provider_name") or "").strip()
        if not provider_choice and not provider_name:
            raise forms.ValidationError("Please select a provider or enter a provider name.")
        return cleaned

    def save(self, commit=True):
        instance = super().save(commit=False)
        provider_choice = self.cleaned_data.get("provider_choice")
        provider_name = (self.cleaned_data.get("provider_name") or "").strip()

        if provider_choice:
            # Attach provider user and set a display name for convenience
            instance.provider = provider_choice.user
            display_name = (
                getattr(provider_choice, "company_name", None)
                or provider_choice.user.get_full_name()
                or provider_choice.user.get_username()
            )
            instance.provider_name = display_name
        else:
            instance.provider_name = provider_name

        if commit:
            instance.save()
        return instance
