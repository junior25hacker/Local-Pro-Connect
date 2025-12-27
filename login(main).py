from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import CustomUser, PhoneOTP
import random
from django.utils import timezone
from datetime import timedelta

# Utility function to send OTP (simulate here)
def send_otp(phone):
    otp = f"{random.randint(100000, 999999)}"
    obj, created = PhoneOTP.objects.update_or_create(phone=phone, defaults={'otp': otp, 'verified': False, 'created_at': timezone.now()})
    print(f"Sending OTP {otp} to phone {phone} (simulate)")
    return otp

# Signup view
def signup_view(request):
    if request.method == 'POST':
        phone = request.POST.get('phone')
        full_name = request.POST.get('full_name')
        password = request.POST.get('password')
        account_type = request.POST.get('account_type')  # 'customer' or 'provider'

        if CustomUser.objects.filter(phone=phone).exists():
            return JsonResponse({'error': 'Phone already registered'}, status=400)

        user = CustomUser.objects.create_user(phone=phone, full_name=full_name, password=password, account_type=account_type)
        send_otp(phone)
        return JsonResponse({'message': 'User created. OTP sent for verification.'})
    return render(request, 'accounts/signup.html')


# OTP verification view
def verify_otp_view(request):
    if request.method == 'POST':
        phone = request.POST.get('phone')
        otp = request.POST.get('otp')

        try:
            otp_obj = PhoneOTP.objects.get(phone=phone)
        except PhoneOTP.DoesNotExist:
            return JsonResponse({'error': 'OTP not found for this phone'}, status=400)

        # OTP expires after 5 minutes
        if timezone.now() > otp_obj.created_at + timedelta(minutes=5):
            return JsonResponse({'error': 'OTP expired'}, status=400)

        if otp_obj.otp == otp:
            otp_obj.verified = True
            otp_obj.save()
            return JsonResponse({'message': 'Phone verified successfully'})
        else:
            return JsonResponse({'error': 'Invalid OTP'}, status=400)

    return render(request, 'accounts/verify_otp.html')


# Login view (phone + password)
def login_view(request):
    if request.method == 'POST':
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        user = authenticate(request, phone=phone, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({'message': 'Logged in successfully'})
        else:
            return JsonResponse({'error': 'Invalid credentials'}, status=400)
    return render(request, 'accounts/login.html')


# Logout view
def logout_view(request):
    logout(request)
    return redirect('/')