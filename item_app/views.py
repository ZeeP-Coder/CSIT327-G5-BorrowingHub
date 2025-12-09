from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from dashboard_app.models import Item
from registration_app.models import TblUser

def item_detail(request, item_id):
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, 'Please log in to view item details.')
        return redirect('login_app:login')
    
    # Get the logged-in user
    try:
        user = TblUser.objects.get(id=user_id)
    except TblUser.DoesNotExist:
        messages.error(request, 'User not found.')
        return redirect('login_app:login')
    
    item = get_object_or_404(Item, id=item_id)
    
    context = {
        'item': item,
        'user': user,
    }
    
    return render(request, 'item_app/item.html', context)
