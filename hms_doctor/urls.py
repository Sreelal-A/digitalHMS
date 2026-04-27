from django.urls import path
from . import views
urlpatterns = [
    path('doctorHome/',views.doctorHome,name='doctorHome'),
    path('appointmentFD/',views.appointmentFD,name='appointmentFD'),
    path('create_prescription/<int:id>/',views.create_prescription,name='create_prescription'),
    path('prescriptionFetch/<int:id>',views.prescriptionFetch,name='prescriptionFetch'),
    path('addTest/<int:id>/',views.addTest,name='addTest'),
    path('PTedit/<int:id>/',views.PTedit,name='PTedit'),
    # AJAX
    path("api/medicines/", views.medicine_search, name="medicine_search"),
    path("api/tests/", views.test_search, name="test_search"),
    # ------------------------------------------------------
    path('patient-history/<int:id>/',views.patient_history,name='patient_history'),
    path('completed_reports/', views.doctor_completed_reports, name='doctor_completed_reports'),
    # path('completed_reports/live/', views.doctor_completed_reports_live, name='doctor_completed_reports_live'),
]