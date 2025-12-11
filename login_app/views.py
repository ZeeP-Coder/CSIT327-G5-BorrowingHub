from django.shortcuts import render, redirect
from django.contrib.auth.hashers import check_password
from django.contrib import messages
from registration_app.models import TblUser

def login_view(request):
    if request.session.get('user_id'):
        return redirect('dashboard_app:dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        try:
            user = TblUser.objects.get(username=username)
            
            if check_password(password, user.password):
                request.session['user_id'] = user.id
                request.session['username'] = user.username
                request.session['email'] = user.email
                messages.success(request, f'Welcome back, {username}!')
                return redirect('dashboard_app:dashboard')
            else:
                messages.error(request, 'Invalid username or password.')
        except TblUser.DoesNotExist:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'login_app/login.html')

def logout_view(request):
    # Clear any existing messages before logout
    storage = messages.get_messages(request)
    storage.used = True
    
    request.session.flush()
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login_app:login')