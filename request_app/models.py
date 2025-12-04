from django.db import models
from django.utils import timezone


class BorrowRequest(models.Model):
	STATUS_CHOICES = [
		('Pending', 'Pending'),
		('Approved', 'Approved'),
		('Rejected', 'Rejected'),
	]

	item = models.ForeignKey('dashboard_app.Item', on_delete=models.CASCADE)
	borrower = models.ForeignKey('registration_app.TblUser', on_delete=models.CASCADE)
	request_date = models.DateTimeField(auto_now_add=True)
	due_date = models.DateField(null=True, blank=True)
	status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')

	class Meta:
		db_table = 'dashboard_app_borrowrequest'  # Preserve existing table name

	def is_overdue(self):
		if self.due_date and self.status == 'Approved':
			return timezone.now().date() > self.due_date
		return False

	def __str__(self):
		return f"{self.borrower.username} -> {self.item.name} ({self.status})"


class RequestRecord(models.Model):
	ACTION_CHOICES = [
		('Approved', 'Approved'),
		('Rejected', 'Rejected'),
	]

	borrow_request = models.ForeignKey(BorrowRequest, on_delete=models.CASCADE)
	action = models.CharField(max_length=32, choices=ACTION_CHOICES)
	performed_by = models.ForeignKey('registration_app.TblUser', on_delete=models.SET_NULL, null=True, blank=True)
	performed_at = models.DateTimeField(default=timezone.now)
	note = models.TextField(blank=True)

	def __str__(self):
		return f"{self.action} - {self.borrow_request} by {self.performed_by}"

