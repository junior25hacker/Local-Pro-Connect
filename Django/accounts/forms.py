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
    username = forms.CharField(max_length=150, required=False)
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=150, required=False)
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not username:
            return username  # Will be generated from email in the view
        from django.contrib.auth.models import User
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('A user with that username already exists.')
        return username
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise forms.ValidationError('Email address is required.')
        from django.contrib.auth.models import User
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('An account with this email already exists.')
        return email

    def clean_password1(self):
        password = self.cleaned_data.get('password1')
        if password and len(password) < 7:
            raise forms.ValidationError('Password must be at least 7 characters long.')
        return password

    def clean(self):
        cleaned = super().clean()
        pw1 = cleaned.get('password1')
        pw2 = cleaned.get('password2')
        if pw1 and pw2 and pw1 != pw2:
            raise forms.ValidationError('Passwords do not match')
        return cleaned


class ProviderRegistrationForm(UserRegistrationForm):
    company_name = forms.CharField(max_length=255, required=False)
    service_type = forms.ChoiceField(choices=ProviderProfile.SERVICE_CHOICES, required=True)
    service_type_other = forms.CharField(max_length=100, required=False, label='Specify Service Type')
    phone = forms.CharField(max_length=20, required=False)
    business_address = forms.CharField(max_length=255, required=False)
    city = forms.CharField(max_length=100, required=True)
    state = forms.CharField(max_length=50, required=True)
    zip_code = forms.CharField(max_length=10, required=False)
    bio = forms.CharField(widget=forms.Textarea, required=False)
    years_experience = forms.IntegerField(min_value=0, required=False)
    
    def clean_service_type_other(self):
        service_type = self.cleaned_data.get('service_type')
        service_type_other = self.cleaned_data.get('service_type_other', '').strip()
        
        if service_type == 'other' and not service_type_other:
            raise forms.ValidationError('Please specify your service type when selecting "Other".')
        
        return service_type_other
    
    def clean_years_experience(self):
        years = self.cleaned_data.get('years_experience')
        if years is None or years == '':
            return 0
        if years < 0:
            raise forms.ValidationError("Years of experience can't be negative")
        return years


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
