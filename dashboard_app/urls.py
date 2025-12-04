from django.urls import path
from . import views

app_name = 'dashboard_app'

urlpatterns = [
	path('', views.dashboard_view, name='dashboard'),
	path('profile/', views.profile_view, name='profile'),
]
