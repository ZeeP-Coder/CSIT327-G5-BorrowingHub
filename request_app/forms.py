from django import forms
from django.utils import timezone
from .models import BorrowRequest


class BorrowRequestForm(forms.ModelForm):
	due_date = forms.DateField(
		widget=forms.DateInput(attrs={'type': 'date'}),
		required=True,
		label="Due Date"
	)

	class Meta:
		model = BorrowRequest
		fields = ['due_date']

	def clean_due_date(self):
		due_date = self.cleaned_data.get('due_date')
		if due_date:
			today = timezone.now().date()
			if due_date < today:
				raise forms.ValidationError("Return date cannot be in the past. Please select today or a future date.")
			# Optionally, you can also add a maximum date limit
			# max_date = today + timezone.timedelta(days=365)
			# if due_date > max_date:
			#     raise forms.ValidationError("Return date cannot be more than 1 year from today.")
		return due_date
