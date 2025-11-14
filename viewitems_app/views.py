from django.shortcuts import render, redirect
from django.contrib import messages
from registration_app.models import TblUser
from dashboard_app.models import Item

# Use the same categories you provided
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

    # Handle POST actions (edit / delete)
    if request.method == 'POST':
        action = request.POST.get('action')
        item_id = request.POST.get('item_id')

        try:
            item = Item.objects.get(id=item_id)
        except (Item.DoesNotExist, TypeError, ValueError):
            messages.error(request, "Item not found.")
            return redirect('viewitems_app:view_items')

        # Ownership check
        if item.owner_id != user.id:
            messages.error(request, "You cannot modify another user's item.")
            return redirect('viewitems_app:view_items')

        if action == 'edit':
            # Update fields
            item.name = request.POST.get('name', item.name)
            item.description = request.POST.get('description', item.description)

            # categories: multi-checkbox
            categories = request.POST.getlist('category')
            if categories:
                item.category = ', '.join(categories)

            qty = request.POST.get('quantity')
            try:
                item.quantity = int(qty) if qty is not None else item.quantity
            except ValueError:
                # keep old value if invalid
                pass

            item.is_available = 'is_available' in request.POST

            # Optional: replace image if uploaded
            if 'image' in request.FILES:
                item.image = request.FILES['image']

            item.save()
            messages.success(request, f'"{item.name}" updated successfully.')
            return redirect('viewitems_app:view_items')

        elif action == 'delete':
            name = item.name
            item.delete()
            messages.success(request, f'"{name}" deleted successfully.')
            return redirect('viewitems_app:view_items')

    # GET - list only user's items
    items = Item.objects.filter(owner_id=user.id).order_by('-created_at')

    context = {
        'user': user,
        'items': items,
        'CATEGORY_CHOICES': CATEGORY_CHOICES,
    }
    return render(request, 'viewitems_app/viewitems.html', context)
