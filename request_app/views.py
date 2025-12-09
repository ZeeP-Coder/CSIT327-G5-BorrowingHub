from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from .models import BorrowRequest
from .forms import BorrowRequestForm
from registration_app.models import TblUser
from dashboard_app.models import Item


def manage_borrow_request(request, request_id, action):
	"""
	Approve or reject a borrow request.
	`action` should be either 'approve' or 'reject'.
	"""
	# Check login
	user_id = request.session.get('user_id')
	if not user_id:
		messages.error(request, "Please log in to continue.")
		return redirect('login_app:login')

	user = get_object_or_404(TblUser, id=user_id)

	borrow_request = get_object_or_404(BorrowRequest, id=request_id)
	item = borrow_request.item

	# SECURITY CHECK: Only item owner can approve/reject
	if item.owner_id != user.id:
		messages.error(request, "You are not allowed to manage this request.")
		return redirect('dashboard_app:dashboard')

	if action == 'approve':
		borrow_request.status = 'Approved'
		item.is_available = False
		item.save()
		borrow_request.save()
		messages.success(request, f"Borrow request for '{item.name}' approved!")
		try:
			from .models import RequestRecord
			RequestRecord.objects.create(borrow_request=borrow_request, action='Approved', performed_by=user)
		except Exception:
			pass

	elif action == 'reject':
		borrow_request.status = 'Rejected'
		borrow_request.save()
		messages.success(request, f"Borrow request for '{item.name}' rejected!")
		try:
			from .models import RequestRecord
			RequestRecord.objects.create(borrow_request=borrow_request, action='Rejected', performed_by=user)
		except Exception:
			pass

	else:
		messages.error(request, "Invalid action.")

	return redirect('dashboard_app:dashboard')


def approve_borrow_request_ajax(request, request_id):
	"""Approve a borrow request via POST (AJAX). Returns JSON."""
	if request.method != 'POST':
		return JsonResponse({'success': False, 'error': 'POST required'}, status=405)

	user_id = request.session.get('user_id')
	if not user_id:
		return JsonResponse({'success': False, 'error': 'login required'}, status=403)

	user = get_object_or_404(TblUser, id=user_id)
	borrow_request = get_object_or_404(BorrowRequest, id=request_id)
	item = borrow_request.item

	if item.owner_id != user.id:
		return JsonResponse({'success': False, 'error': 'not owner'}, status=403)

	borrow_request.status = 'Approved'
	item.is_available = False
	item.save()
	borrow_request.save()

	# Record history entry
	try:
		from .models import RequestRecord
		RequestRecord.objects.create(borrow_request=borrow_request, action='Approved', performed_by=user)
	except Exception:
		pass

	return JsonResponse({'success': True, 'message': 'Approved'})


def reject_borrow_request_ajax(request, request_id):
	"""Reject a borrow request via POST (AJAX). Returns JSON."""
	if request.method != 'POST':
		return JsonResponse({'success': False, 'error': 'POST required'}, status=405)

	user_id = request.session.get('user_id')
	if not user_id:
		return JsonResponse({'success': False, 'error': 'login required'}, status=403)

	user = get_object_or_404(TblUser, id=user_id)
	borrow_request = get_object_or_404(BorrowRequest, id=request_id)
	item = borrow_request.item

	if item.owner_id != user.id:
		return JsonResponse({'success': False, 'error': 'not owner'}, status=403)

	borrow_request.status = 'Rejected'
	borrow_request.save()

	# Record history entry
	try:
		from .models import RequestRecord
		RequestRecord.objects.create(borrow_request=borrow_request, action='Rejected', performed_by=user)
	except Exception:
		pass

	return JsonResponse({'success': True, 'message': 'Rejected'})


def borrow_request_list(request):
	"""Redirect to history page - this view is kept for URL compatibility."""
	return redirect('request_app:history')


def borrow_request_create(request, item_id):
	"""Create a borrow request for an item (separate page/form)."""
	user_id = request.session.get('user_id')
	if not user_id:
		messages.error(request, 'Please log in to request an item.')
		return redirect('login_app:login')

	user = get_object_or_404(TblUser, id=user_id)
	item = get_object_or_404(Item, id=item_id)

	# Prevent owner from borrowing their own item
	if item.owner_id == user.id:
		messages.error(request, "You cannot borrow your own item.")
		return redirect('dashboard_app:dashboard')

	# Prevent duplicate pending requests
	if BorrowRequest.objects.filter(item=item, borrower=user, status='Pending').exists():
		messages.error(request, "You already have a pending request for this item.")
		return redirect('dashboard_app:dashboard')

	if not item.is_available:
		messages.error(request, "Item is not available.")
		return redirect('dashboard_app:dashboard')

	if request.method == 'POST':
		form = BorrowRequestForm(request.POST)
		if form.is_valid():
			br = form.save(commit=False)
			br.item = item
			br.borrower = user
			br.status = 'Pending'
			br.save()
			messages.success(request, f'Borrow request for "{item.name}" submitted successfully!')
			return redirect('request_app:borrow_request_list')
		else:
			messages.error(request, f"Invalid due date: {form.errors}")
	else:
		form = BorrowRequestForm()

	return render(request, 'request_app/request_form.html', {'form': form, 'item': item, 'user': user})


def borrow_request_detail(request, pk):
	"""Return an HTML snippet with borrow request details suitable for modal display."""
	br = get_object_or_404(BorrowRequest, id=pk)
	user = None
	user_id = request.session.get('user_id')
	if user_id:
		try:
			user = TblUser.objects.get(id=user_id)
		except TblUser.DoesNotExist:
			user = None
	return render(request, 'request_app/borrow_request_detail.html', {'br': br, 'user': user})


def history(request):
	"""Show history of requests for the logged-in user.

	Owners see incoming requests for their items; borrowers see their own requests.
	"""
	user_id = request.session.get('user_id')
	if not user_id:
		messages.error(request, 'Please log in to view request history.')
		return render(request, 'request_app/history.html', {'incoming': [], 'mine': []})

	user = get_object_or_404(TblUser, id=user_id)
	incoming = BorrowRequest.objects.filter(item__owner=user).order_by('-request_date')
	mine = BorrowRequest.objects.filter(borrower=user).order_by('-request_date')
	# Also show recent action records if available
	records = None
	try:
		from .models import RequestRecord
		# avoid querying if migrations not applied: check table exists first
		from django.db import connection
		tables = connection.introspection.table_names()
		if RequestRecord._meta.db_table in tables:
			# combine incoming and mine querysets' ids to avoid union on DBs that don't support it
			rq_ids = list(incoming.values_list('id', flat=True)) + list(mine.values_list('id', flat=True))
			if rq_ids:
				records = RequestRecord.objects.filter(borrow_request_id__in=rq_ids).order_by('-performed_at')[:50]
			else:
				records = None
		else:
			records = None
	except Exception:
		records = None

	return render(request, 'request_app/history.html', {'incoming': incoming, 'mine': mine, 'user': user, 'records': records})

