from django import forms
from .models import ProviderProfile


class ProviderProfileForm(forms.ModelForm):
    class Meta:
        model = ProviderProfile
        fields = [
            'company_name', 'service_type', 'phone', 'business_address', 'city', 'state', 'zip_code',
            'service_description', 'bio', 'years_experience', 'profile_picture'
        ]

    def clean_years_experience(self):
        years = self.cleaned_data.get('years_experience')
        if years is None:
            return 0
        if years < 0:
            raise forms.ValidationError("Years of experience can't be negative")
        return years


class UserRegistrationForm(forms.Form):
    username = forms.CharField(max_length=150)
    email = forms.EmailField(required=False)
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=150, required=False)
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)

    def clean_username(self):
        username = self.cleaned_data.get('username')
        from django.contrib.auth.models import User
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('A user with that username already exists.')
        return username

    def clean(self):
        cleaned = super().clean()
        pw1 = cleaned.get('password1')
        pw2 = cleaned.get('password2')
        if pw1 and pw1 != pw2:
            raise forms.ValidationError('Passwords do not match')
        return cleaned


class ProviderRegistrationForm(UserRegistrationForm):
    company_name = forms.CharField(max_length=255, required=False)
    service_type = forms.ChoiceField(choices=ProviderProfile.SERVICE_CHOICES, initial='other', required=True)
    phone = forms.CharField(max_length=20, required=False)
    business_address = forms.CharField(max_length=255, required=False)
    city = forms.CharField(max_length=100, required=False)
    state = forms.CharField(max_length=50, required=False)
    zip_code = forms.CharField(max_length=10, required=False)
    bio = forms.CharField(widget=forms.Textarea, required=False)
    years_experience = forms.IntegerField(min_value=0, required=True, initial=0)


class UserLoginForm(forms.Form):
    """Professional user login form with validation"""
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your username',
            'autocomplete': 'username',
            'required': True
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password',
            'autocomplete': 'current-password',
            'required': True
        })
    )
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email (optional)',
            'autocomplete': 'email'
        })
    )

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not username:
            raise forms.ValidationError('Username is required.')
        return username

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if not password:
            raise forms.ValidationError('Password is required.')
        return password


class ProviderLoginForm(UserLoginForm):
    """Provider login form (same fields as user for consistency)"""
    pass
