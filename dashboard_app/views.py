from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden
from registration_app.models import TblUser
from dashboard_app.models import Item
from request_app.models import BorrowRequest
from request_app.forms import BorrowRequestForm
from .supabase_client import upload_item_image
from .supabase_client import supabase

# -----------------------------
# DASHBOARD VIEW (All Items)
# -----------------------------
def dashboard_view(request):
    # Check login
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, 'Please log in to access the dashboard.')
        return redirect('login_app:login')

    # Fetch logged-in user
    try:
        user = TblUser.objects.get(id=user_id)
    except TblUser.DoesNotExist:
        request.session.flush()
        messages.error(request, 'Invalid session. Please log in again.')
        return redirect('login_app:login')

    if request.method == 'POST':
        # ----- EDIT / DELETE -----
        if 'action' in request.POST and 'item_id' in request.POST:
            action = request.POST.get('action')
            item_id = request.POST.get('item_id')
            try:
                item = Item.objects.get(id=item_id)
            except Item.DoesNotExist:
                messages.error(request, "Item not found.")
                return redirect('dashboard_app:dashboard')

            # SECURITY CHECK — Only owner can modify
            if item.owner_id != user.id:
                messages.error(request, "You cannot modify another user’s item.")
                return redirect('dashboard_app:dashboard')

            if action == 'edit':
                item.name = request.POST.get('name', item.name)
                item.description = request.POST.get('description', item.description)
                categories = request.POST.getlist('category')
                if categories:
                    item.category = ', '.join(categories)
                item.quantity = request.POST.get('quantity', item.quantity)
                item.is_available = 'is_available' in request.POST
                if 'image' in request.FILES:
                    item.image_url = request.FILES['image']
                item.save()
                messages.success(request, f'"{item.name}" updated successfully!')

            elif action == 'delete':
                item_name = item.name
                item.delete()
                messages.success(request, f'"{item_name}" deleted successfully!')

            return redirect('dashboard_app:dashboard')

        # ----- BORROW REQUEST -----
        elif 'borrow_item_id' in request.POST:
            borrow_item_id = request.POST.get('borrow_item_id')
            try:
                item = Item.objects.get(id=borrow_item_id)
            except Item.DoesNotExist:
                messages.error(request, "Item not found.")
                return redirect('dashboard_app:dashboard')
            
              # Prevent owner from borrowing their own item
            if item.owner_id == user.id:
                messages.error(request, "You cannot borrow your own item.")
                return redirect('dashboard_app:dashboard')
            
                # Prevent duplicate pending requests by same user
            if BorrowRequest.objects.filter(item=item, borrower=user, status='Pending').exists():
                messages.error(request, "You already have a pending request for this item.")
                return redirect('dashboard_app:dashboard')

            if not item.is_available:
                messages.error(request, "Item is already borrowed.")
                return redirect('dashboard_app:dashboard')

            form = BorrowRequestForm(request.POST)
            if form.is_valid():
                borrow_request = form.save(commit=False)
                borrow_request.item = item
                borrow_request.borrower = user
                borrow_request.status = 'Pending'
                borrow_request.save()
                messages.success(request, f'Borrow request for "{item.name}" submitted successfully!')
            else:
                messages.error(request, f"Invalid due date: {form.errors}")

        return redirect('dashboard_app:dashboard')

    # -----------------------------
    # FETCH ITEMS (GET REQUEST)
    # -----------------------------
    items = Item.objects.all().order_by('-created_at')

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

    context = {
        'user': user,
        'items': items,
        'total_items': Item.objects.count(),
        'available_items': Item.objects.filter(is_available=True).count(),
        'borrowed_items': Item.objects.filter(is_available=False).count(),
        'overdue_items': 0,  # Placeholder
        'search_query': search_query,
        'category_filter': category_filter,
        'status_filter': status_filter,
    }

    # Incoming pending borrow requests for this user (owner)
    borrow_requests = BorrowRequest.objects.filter(item__owner=user, status='Pending').order_by('-request_date')
    context['borrow_requests'] = borrow_requests
    context['pending_requests_count'] = borrow_requests.count()
    return render(request, 'dashboard_app/dashboard.html', context)



# -----------------------------
# PROFILE VIEW
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

    return render(request, 'profile_app/profile.html', {'user': user})

# -----------------------------
# ITEM IMAGE UPLOAD HANDLER
# -----------------------------
def add_item(request):
    if request.method == "POST":
        item_name = request.POST.get("item_name")
        description = request.POST.get("description")
        quantity = request.POST.get("quantity")

        image_file = request.FILES.get("image")
        image_url = None

        if image_file:
            # Upload to Supabase
            file_path = f"items/{image_file.name}"
            supabase.storage.from_("item-images").upload(
                file_path,
                image_file.read()
            )
            # Get public URL
            image_url = supabase.storage.from_("item-images").get_public_url(file_path)

        Item.objects.create(
            item_name=item_name,
            description=description,
            quantity=quantity,
            image_url=image_url,
            owner=TblUser.objects.get(id=request.session.get('user_id')), # assign owner
        )

        return redirect("inventory")

    return render(request, "add_item.html")
