from django.urls import path
from . import views

urlpatterns = [
    path('laboratoryHome/',views.laboratoryHome,name='laboratoryHome'),
    path('manage_tests/', views.manage_tests, name='manage_tests'),
    path('delete_test/<int:id>/', views.delete_test, name='delete_test'),
    path('test_list/', views.test_list, name='test_list'),
    path('test_detail/<int:id>/', views.test_detail, name='test_detail'),
    path('completed_reports/', views.completed_reports, name='completed_reports'),
]