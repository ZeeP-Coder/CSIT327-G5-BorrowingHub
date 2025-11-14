from django.db import models
from registration_app.models import TblUser

class Item(models.Model):
    owner = models.ForeignKey(TblUser, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=300, blank=True)
    image = models.ImageField(upload_to='items/', blank=True, null=True)
    quantity = models.PositiveIntegerField(default=1)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
