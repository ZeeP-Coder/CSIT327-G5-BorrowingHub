from django.urls import path
from . import views

app_name = 'profile_app'

urlpatterns = [
    path('', views.profile_view, name='profile'),
    path('change-password/', views.change_password, name='change_password'),
]