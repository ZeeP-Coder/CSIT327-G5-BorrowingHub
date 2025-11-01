from django import forms
from dashboard_app.models import Item

CATEGORY_CHOICES = [
    ('Books', 'Books'),
    ('Electronics', 'Electronics'),
    ('Tools', 'Tools'),
    ('Sports', 'Sports'),
    ('School Supplies', 'School Supplies'),
    ('Board Games', 'Board Games'),
    ('Sports Equipment', 'Sports Equipment'),
    ('Toys & Games', 'Toys & Games'),
    ('Furniture', 'Furniture'),
    ('Kitchen Appliances', 'Kitchen Appliances'),
    ('Cleaning Equipment', 'Cleaning Equipment'),
    ('Miscellaneous / Others', 'Miscellaneous / Others'),
]

class ItemForm(forms.ModelForm):
    category = forms.MultipleChoiceField(
        choices=CATEGORY_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=True
    )

    class Meta:
        model = Item
        fields = ['name', 'description', 'category', 'image', 'quantity', 'is_available']

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
