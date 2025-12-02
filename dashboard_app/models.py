from django.db import models
from django.utils import timezone
from registration_app.models import TblUser

class Item(models.Model):
    owner = models.ForeignKey(TblUser, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=300, blank=True)
    image_url = models.URLField(blank=True, null=True)
    quantity = models.PositiveIntegerField(default=1)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class BorrowRequest(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]

    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    borrower = models.ForeignKey(TblUser, on_delete=models.CASCADE)
    request_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')

    def is_overdue(self):
        if self.due_date and self.status == 'Approved':
            return timezone.now().date() > self.due_date
        return False

    def __str__(self):
        return f"{self.borrower.username} -> {self.item.name} ({self.status})"