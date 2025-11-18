from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings

from registration_app.models import TblUser
from dashboard_app.models import Item

from .supabase_client import upload_item_image

CATEGORY_CHOICES = [
    ('Books', 'Books'),
    ('Electronics', 'Electronics'),
    ('Tools', 'Tools'),
    ('Sports', 'Sports'),
    ('School Supplies', 'School Supplies'),
    ('Board Games', 'Board Games'),
    ('Sports Equipment', 'Sports Equipment'),
    ('Toys & Games', 'Toys & Games'),
    ('Furniture', 'Furniture'),
    ('Kitchen Appliances', 'Kitchen Appliances'),
    ('Cleaning Equipment', 'Cleaning Equipment'),
    ('Miscellaneous / Others', 'Miscellaneous / Others'),
]


def view_items(request):

    # Authentication check
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, "Please log in to view your items.")
        return redirect('login_app:login')

    try:
        user = TblUser.objects.get(id=user_id)
    except TblUser.DoesNotExist:
        request.session.flush()
        messages.error(request, "Invalid session. Please log in again.")
        return redirect('login_app:login')

    # --- POST actions ---
    if request.method == 'POST':
        action = request.POST.get('action')
        item_id = request.POST.get('item_id')

        try:
            item = Item.objects.get(id=item_id)
        except Item.DoesNotExist:
            messages.error(request, "Item not found.")
            return redirect('viewitems_app:view_items')

        # Prevent editing other users' items
        if item.owner_id != user.id:
            messages.error(request, "You cannot modify another user's item.")
            return redirect('viewitems_app:view_items')

        # --- EDIT ITEM ---
        if action == 'edit':

            item.name = request.POST.get('name', item.name)
            item.description = request.POST.get('description', item.description)

            categories = request.POST.getlist('category')
            if categories:
                item.category = ", ".join(categories)

            qty = request.POST.get('quantity')
            try:
                item.quantity = int(qty)
            except:
                pass

            item.is_available = 'is_available' in request.POST

            # ---------- IMAGE UPLOAD FIX ----------
            image_file = request.FILES.get("image_file")
            if image_file:
                item.image_url = upload_item_image(image_file, item.id)

            item.save()
            messages.success(request, f'"{item.name}" updated successfully.')
            return redirect('viewitems_app:view_items')

        # --- DELETE ITEM ---
        elif action == 'delete':
            name = item.name
            item.delete()
            messages.success(request, f'"{name}" deleted successfully.')
            return redirect('viewitems_app:view_items')

    # --- GET: List of items ---
    items = Item.objects.filter(owner_id=user.id).order_by('-created_at')

    return render(request, 'viewitems_app/viewitems.html', {
        'user': user,
        'items': items,
        'CATEGORY_CHOICES': CATEGORY_CHOICES,
    })
