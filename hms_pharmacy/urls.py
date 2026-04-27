from django.urls import path
from . import views
urlpatterns = [
    path('pharmacyHome/',views.pharmacyHome,name='pharmacyHome'),
    path('addMedicine/',views.addMedicine,name='addMedicine'),
    path("updateMedicine/<int:id>/", views.updateMedicine, name="updateMedicine"),
    path('prescriptionFP/',views.prescriptionFP,name='prescriptionFP'),
    path('view_prescription/<int:id>/',views.view_prescription,name='view_prescription'),
    path('lab-reports/', views.lab_reports_pharmacy, name='lab_reports_pharmacy'),

]