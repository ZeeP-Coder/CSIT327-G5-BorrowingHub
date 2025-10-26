from django.urls import path
from . import views

app_name = 'additem_app'

urlpatterns = [
    path('', views.add_item_view, name='add_item'),
]
