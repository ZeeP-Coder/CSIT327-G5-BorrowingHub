from django.shortcuts import render, redirect
from django.contrib import messages
from registration_app.models import TblUser
from .forms import ItemForm

def add_item_view(request):
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, 'Please log in to add an item.')
        return redirect('login_app:login')

    if request.method == 'POST':
        form = ItemForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Item added successfully!')
            return redirect('dashboard_app:dashboard')
    else:
        form = ItemForm()

    return render(request, 'additem_app/add_item.html', {'form': form})
