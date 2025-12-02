from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from dashboard_app.models import BorrowRequest
from registration_app.models import TblUser


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
