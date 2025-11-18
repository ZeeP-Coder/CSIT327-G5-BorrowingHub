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

    image_file = forms.FileField(
        required=False,
        label="Upload Image",
        widget=forms.ClearableFileInput
    )

    image_url = forms.URLField(
        required=False,
        label="Image URL",
        widget=forms.URLInput(attrs={'placeholder': 'https://example.com/image.jpg'})
    )

    class Meta:
        model = Item
        fields = ['name', 'description', 'category', 'image_url', 'quantity', 'is_available']

    def clean_image_file(self):
        image = self.cleaned_data.get('image_file')
        if image is None:
            return None  # no file uploaded, skip validation
        valid_extensions = ['jpg', 'jpeg', 'png', 'webp']
        if not image.name.lower().endswith(tuple(valid_extensions)):
            raise forms.ValidationError("Only JPG, PNG, and WEBP image formats are allowed.")
        return image

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

    def clean(self):
        cleaned_data = super().clean()
        image_file = cleaned_data.get("image_file")
        image_url = cleaned_data.get("image_url")
        if not image_file and not image_url:
            raise forms.ValidationError("Please provide either an image file or an image URL.")
        return cleaned_data
