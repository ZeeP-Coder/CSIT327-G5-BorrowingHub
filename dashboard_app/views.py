from django.shortcuts import render, redirect
from django.contrib import messages
from registration_app.models import TblUser
from dashboard_app.models import Item


# -----------------------------
# DASHBOARD VIEW (with Edit + Delete support)
# -----------------------------
def dashboard_view(request):
    # ✅ Session-based authentication
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

    # --------------------------------
    # 🧾 Handle POST actions (Edit / Delete)
    # --------------------------------
    if request.method == 'POST':
        action = request.POST.get('action')
        item_id = request.POST.get('item_id')

        try:
            item = Item.objects.get(id=item_id)
        except Item.DoesNotExist:
            messages.error(request, "Item not found.")
            return redirect('dashboard_app:dashboard')

        # 📝 EDIT ITEM
        if action == 'edit':
            item.name = request.POST.get('name', item.name)
            item.description = request.POST.get('description', item.description)

            # ✅ Handle multiple category checkboxes
            categories = request.POST.getlist('category')
            if categories:
                item.category = ', '.join(categories)
            else:
                item.category = request.POST.get('category', item.category)

            item.quantity = request.POST.get('quantity', item.quantity)
            item.is_available = 'is_available' in request.POST

            # ✅ Optional: update image if a new one is uploaded
            if 'image' in request.FILES:
                item.image = request.FILES['image']

            item.save()
            messages.success(request, f'"{item.name}" was updated successfully!')
            return redirect('dashboard_app:dashboard')

        # ❌ DELETE ITEM
        elif action == 'delete':
            name = item.name
            item.delete()
            messages.success(request, f'"{name}" was deleted successfully!')
            return redirect('dashboard_app:dashboard')

    # --------------------------------
    # 🧾 Fetch all items (GET request)
    # --------------------------------
    items = Item.objects.all()

    # 🧠 Search and filter logic
    search_query = request.GET.get('search', '')
    category_filter = request.GET.get('category', '')
    status_filter = request.GET.get('status', '')

    if search_query:
        items = items.filter(name__icontains=search_query)
    if category_filter and category_filter != 'All Categories':
        items = items.filter(category__icontains=category_filter)
    if status_filter and status_filter != 'All Status':
        if status_filter == 'Available':
            items = items.filter(is_available=True)
        elif status_filter == 'Borrowed':
            items = items.filter(is_available=False)

    # 📊 Dashboard stats
    total_items = Item.objects.count()
    available_items = Item.objects.filter(is_available=True).count()
    borrowed_items = Item.objects.filter(is_available=False).count()
    overdue_items = 0  # (optional feature)

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


# -----------------------------
# PROFILE VIEW (fixes the missing reference)
# -----------------------------
def profile_view(request):
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

    context = {'user': user}
    return render(request, 'profile_app/profile.html', context)
