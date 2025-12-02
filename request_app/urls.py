from django.urls import path
from . import views

app_name = 'request_app'

urlpatterns = [
    path('', views.history, name='history'),
]
