from django.shortcuts import render, redirect
from django.contrib import messages
from registration_app.models import TblUser
from .forms import ItemForm
from dashboard_app.supabase_client import upload_item_image  # ensure this path matches where you put supabase_client

def add_item_view(request):
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, 'Please log in to add an item.')
        return redirect('login_app:login')

    # Get user information
    try:
        user = TblUser.objects.get(id=user_id)
    except TblUser.DoesNotExist:
        messages.error(request, 'User not found.')
        return redirect('login_app:login')

    if request.method == 'POST':
        form = ItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.owner_id = user_id

            # Save phone number to the item
            contact_phone = request.POST.get('contact_phone')
            if contact_phone:
                item.phone_number = contact_phone

            categories = form.cleaned_data.get('category', [])
            item.category = ', '.join(categories)

            # Save immediately to get item.id (needed for filename)
            item.save()

            # Upload image file to Supabase if provided
            image_file = form.cleaned_data.get('image_file')
            if image_file:
                item.image_url = upload_item_image(image_file, item.id)
                item.save()

            messages.success(request, 'Item added successfully!')
            return redirect('dashboard_app:dashboard')
    else:
        form = ItemForm()

    return render(request, 'additem_app/add_item.html', {'form': form, 'user': user})
