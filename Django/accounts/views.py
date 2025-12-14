
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages, auth

def home(request):
    return render(request, 'pages/index.html')

def auth_view(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if action == 'signup':
            if User.objects.filter(email=email).exists():
                messages.error(request, 'User already exists. Please sign in.')
                return render(request, 'login.html', {'switch_to': 'signin'})
            else:
                username = email.split('@')[0]
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()
                messages.success(request, 'Account has been created successfully. Please sign in.')
                return render(request, 'login.html', {'switch_to': 'signin'})

        elif action == 'signin':
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                messages.error(request, "Email doesn't have an account yet. Please sign up.")
                return render(request, 'register-user.html', {'switch_to': 'signup'})

            user = auth.authenticate(username=user.username, password=password)
            if user is not None:
                auth.login(request, user)
                messages.success(request, 'Signed in successfully.')
                return redirect('home')
            else:
                messages.error(request, 'Wrong password. Please try again.')
                return render(request, 'login.html', {'switch_to': 'signin'})

    return render(request, 'auth_choice.html')
