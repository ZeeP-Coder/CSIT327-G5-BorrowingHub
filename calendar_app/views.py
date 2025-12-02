from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from dashboard_app.models import BorrowRequest
from registration_app.models import TblUser
from django.http import JsonResponse


def calendar_events(request):
	"""Return JSON events for FullCalendar: upcoming approved borrow requests for the user.

	Includes events where the user is the borrower (items they must return) and
	events where the user is the owner (items borrowed from them are due back).
	"""
	user_id = request.session.get('user_id')
	if not user_id:
		# return an empty array when unauthenticated so FullCalendar receives a list
		return JsonResponse([], safe=False)

	user = get_object_or_404(TblUser, id=user_id)

	today = timezone.now().date()
	upcoming_limit = today + timedelta(days=365)  # show up to 1 year ahead

	borrower_qs = BorrowRequest.objects.filter(
		borrower=user, status='Approved', due_date__isnull=False, due_date__gte=today, due_date__lte=upcoming_limit
	).order_by('due_date')

	owner_qs = BorrowRequest.objects.filter(
		item__owner=user, status='Approved', due_date__isnull=False, due_date__gte=today, due_date__lte=upcoming_limit
	).order_by('due_date')

	events = []
	for br in borrower_qs:
		events.append({
			'id': f'br-{br.id}',
			'title': f'Return: {br.item.name}',
			'start': br.due_date.isoformat(),
			'allDay': True,
			'color': '#f59e0b',  # amber for borrower returns
			'extendedProps': {
				'type': 'borrower',
				'item_id': br.item.id,
				'borrow_request_id': br.id,
			}
		})

	for br in owner_qs:
		events.append({
			'id': f'ow-{br.id}',
			'title': f'Due back: {br.item.name} ({br.borrower.username})',
			'start': br.due_date.isoformat(),
			'allDay': True,
			'color': '#ef4444',  # red for owner due back
			'extendedProps': {
				'type': 'owner',
				'item_id': br.item.id,
				'borrow_request_id': br.id,
			}
		})

	return JsonResponse(events, safe=False)


def calendar_view(request):
	"""Simple calendar-like view listing upcoming due dates for the logged-in user's borrowed items."""
	user_id = request.session.get('user_id')
	if not user_id:
		messages.error(request, 'Please log in to view calendar.')
		return render(request, 'calendar_app/calendar.html', {'events': []})

	user = get_object_or_404(TblUser, id=user_id)

	today = timezone.now().date()
	upcoming_limit = today + timedelta(days=30)

	# Fetch approved borrow requests for this user where due_date is within next 30 days
	events = BorrowRequest.objects.filter(borrower=user, status='Approved', due_date__isnull=False, due_date__gte=today, due_date__lte=upcoming_limit).order_by('due_date')

	# Also include items the user owns that are due (if owner wants to see returns)
	owner_events = BorrowRequest.objects.filter(item__owner=user, status='Approved', due_date__isnull=False, due_date__gte=today, due_date__lte=upcoming_limit).order_by('due_date')

	return render(request, 'calendar_app/calendar.html', {'events': events, 'owner_events': owner_events, 'user': user})
