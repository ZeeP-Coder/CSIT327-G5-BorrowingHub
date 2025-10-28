from django import forms
from dashboard_app.models import Item 

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['name', 'description', 'category', 'image', 'quantity', 'is_available']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter item name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describe the item'
            }),
            'category': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Category'
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1
            }),
            'is_available': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }


    def clean_name(self):
        name = self.cleaned_data.get('name')
        if len(name.strip()) < 3:
            raise forms.ValidationError("Item name must be at least 3 characters long.")
        return name

    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        if quantity is None or quantity < 1:
            raise forms.ValidationError("Quantity must be at least 1.")
        return quantity

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            valid_extensions = ['jpg', 'jpeg', 'png', 'webp']
            if not image.name.lower().endswith(tuple(valid_extensions)):
                raise forms.ValidationError("Only JPG, PNG, and WEBP image formats are allowed.")
        return image