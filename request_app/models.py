from django.db import models
from django.utils import timezone


class RequestRecord(models.Model):
	ACTION_CHOICES = [
		('Approved', 'Approved'),
		('Rejected', 'Rejected'),
	]

	borrow_request = models.ForeignKey('dashboard_app.BorrowRequest', on_delete=models.CASCADE)
	action = models.CharField(max_length=32, choices=ACTION_CHOICES)
	performed_by = models.ForeignKey('registration_app.TblUser', on_delete=models.SET_NULL, null=True, blank=True)
	performed_at = models.DateTimeField(default=timezone.now)
	note = models.TextField(blank=True)

	def __str__(self):
		return f"{self.action} - {self.borrow_request} by {self.performed_by}"
