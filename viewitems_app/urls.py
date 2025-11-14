from django.urls import path
from . import views

app_name = "viewitems_app"

urlpatterns = [
    path('', views.view_items, name='view_items'),
]
