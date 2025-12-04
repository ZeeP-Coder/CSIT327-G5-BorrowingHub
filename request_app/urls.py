from django.urls import path
from . import views

app_name = 'request_app'

urlpatterns = [
	path('history/', views.history, name='history'),
	path('list/', views.borrow_request_list, name='borrow_request_list'),
	path('create/<int:item_id>/', views.borrow_request_create, name='borrow_request_create'),
	path('detail/<int:pk>/', views.borrow_request_detail, name='borrow_request_detail'),
	path('manage/<int:request_id>/<str:action>/', views.manage_borrow_request, name='manage_borrow_request'),
	# AJAX endpoints for approving/rejecting requests via POST
	path('approve/<int:request_id>/', views.approve_borrow_request_ajax, name='approve_borrow_request_ajax'),
	path('reject/<int:request_id>/', views.reject_borrow_request_ajax, name='reject_borrow_request_ajax'),
]
