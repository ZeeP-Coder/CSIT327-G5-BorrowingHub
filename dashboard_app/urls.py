from django.urls import path
from . import views

app_name = 'dashboard_app'

urlpatterns = [
    path('requests/', views.borrow_request_list, name='borrow_request_list'),
    path('requests/create/<int:item_id>/', views.borrow_request_create, name='borrow_request_create'),
    path('requests/detail/<int:pk>/', views.borrow_request_detail, name='borrow_request_detail'),
    path('', views.dashboard_view, name='dashboard'),
    path('profile/', views.profile_view, name='profile'),
    path('borrow-request/<int:request_id>/<str:action>/', views.manage_borrow_request, name='manage_borrow_request'),
    # AJAX endpoints for approving/rejecting requests via POST
    path('requests/approve/<int:request_id>/', views.approve_borrow_request_ajax, name='approve_borrow_request_ajax'),
    path('requests/reject/<int:request_id>/', views.reject_borrow_request_ajax, name='reject_borrow_request_ajax'),
]
