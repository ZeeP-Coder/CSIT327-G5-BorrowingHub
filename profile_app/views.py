from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import check_password, make_password
from registration_app.models import TblUser
from dashboard_app.models import Item
from request_app.models import BorrowRequest


def profile_view(request):
	"""Display user profile with statistics."""
	user_id = request.session.get('user_id')
	if not user_id:
		messages.error(request, 'Please log in to view your profile.')
		return redirect('login_app:login')
	
	try:
		user = TblUser.objects.get(id=user_id)
	except TblUser.DoesNotExist:
		request.session.flush()
		messages.error(request, 'Invalid session. Please log in again.')
		return redirect('login_app:login')
	
	# Get statistics
	items_count = Item.objects.filter(owner_id=user_id).count()
	requests_count = BorrowRequest.objects.filter(borrower_id=user_id, status='Pending').count()
	
	context = {
		'user': user,
		'items_count': items_count,
		'requests_count': requests_count,
	}
	
	return render(request, 'profile_app/profile.html', context)


def change_password(request):
	"""Handle password change requests."""
	if request.method != 'POST':
		return redirect('profile_app:profile')
	
	user_id = request.session.get('user_id')
	if not user_id:
		messages.error(request, 'Please log in to change your password.')
		return redirect('login_app:login')
	
	try:
		user = TblUser.objects.get(id=user_id)
	except TblUser.DoesNotExist:
		messages.error(request, 'User not found.')
		return redirect('login_app:login')
	
	current_password = request.POST.get('current_password')
	new_password = request.POST.get('new_password')
	confirm_password = request.POST.get('confirm_password')
	
	# Verify current password using Django's check_password
	if not check_password(current_password, user.password):
		messages.error(request, 'Current password is incorrect.')
		return redirect('profile_app:profile')
	
	# Verify new passwords match
	if new_password != confirm_password:
		messages.error(request, 'New passwords do not match.')
		return redirect('profile_app:profile')
	
	# Verify new password is different from current
	if current_password == new_password:
		messages.error(request, 'New password must be different from current password.')
		return redirect('profile_app:profile')
	
	# Verify password strength (minimum 8 characters to match registration)
	if len(new_password) < 8:
		messages.error(request, 'Password must be at least 8 characters long.')
		return redirect('profile_app:profile')
	
	# Update password using Django's make_password
	user.password = make_password(new_password)
	user.save()
	
	messages.success(request, 'Password changed successfully!')
	return redirect('profile_app:profile')
