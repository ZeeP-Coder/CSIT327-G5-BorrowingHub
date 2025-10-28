from django.db import models

# Create your models here.
image = models.ImageField(upload_to='item_images/', blank=True, null=True)