from django import forms
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
