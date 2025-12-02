from django.contrib import admin
from .models import RequestRecord

@admin.register(RequestRecord)
class RequestRecordAdmin(admin.ModelAdmin):
	list_display = ('borrow_request', 'action', 'performed_by', 'performed_at')
	list_filter = ('action', 'performed_at')
	search_fields = ('borrow_request__item__name', 'performed_by__username')
