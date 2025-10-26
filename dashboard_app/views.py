from django.shortcuts import render, redirect
from django.contrib import messages
from registration_app.models import TblUser
from dashboard_app.models import Item

def dashboard_view(request):
    # Check session-based authentication
    user_id = request.session.get('user_id')
    
    if not user_id:
        messages.error(request, 'Please log in to access the dashboard.')
        return redirect('login_app:login')
    
    try:
        user = TblUser.objects.get(id=user_id)
    except TblUser.DoesNotExist:
        request.session.flush()
        messages.error(request, 'Invalid session. Please log in again.')
        return redirect('login_app:login')

    # 🧭 Get all items initially
    items = Item.objects.all()

    # 🕵️‍♀️ Handle search and filter queries
    search_query = request.GET.get('search', '')
    category_filter = request.GET.get('category', '')
    status_filter = request.GET.get('status', '')

    if search_query:
        items = items.filter(name__icontains=search_query)
    if category_filter and category_filter != 'All Categories':
        items = items.filter(category=category_filter)
    if status_filter and status_filter != 'All Status':
        if status_filter == 'Available':
            items = items.filter(is_available=True)
        elif status_filter == 'Borrowed':
            items = items.filter(is_available=False)

    # 📊 Count summaries
    total_items = Item.objects.count()
    available_items = Item.objects.filter(is_available=True).count()
    borrowed_items = Item.objects.filter(is_available=False).count()
    overdue_items = 0  # (optional logic later)

    context = {
        'user': user,
        'items': items,
        'total_items': total_items,
        'available_items': available_items,
        'borrowed_items': borrowed_items,
        'overdue_items': overdue_items,
        'search_query': search_query,
        'category_filter': category_filter,
        'status_filter': status_filter,
    }

    return render(request, 'dashboard_app/dashboard.html', context)

def profile_view(request):
    # Check session-based authentication
    user_id = request.session.get('user_id')
    
    if not user_id:
        messages.error(request, 'Please log in to access your profile.')
        return redirect('login_app:login')
    
    try:
        user = TblUser.objects.get(id=user_id)
    except TblUser.DoesNotExist:
        request.session.flush()
        messages.error(request, 'Invalid session. Please log in again.')
        return redirect('login_app:login')
    
    context = {
        'user': user,
    }
    return render(request, 'profile_app/profile.html', context)