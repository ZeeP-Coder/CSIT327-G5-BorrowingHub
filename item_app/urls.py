from django.urls import path
from . import views

app_name = 'item_app'

urlpatterns = [
    path('<int:item_id>/', views.item_detail, name='item_detail'),
]
