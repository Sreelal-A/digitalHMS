from django.urls import path
from . import views

urlpatterns = [
    path("billingHome/", views.billingHome, name="billingHome"),

    path("patients/", views.billing_patient_list, name="billing_patient_list"),
    path("generate/<int:appointment_id>/", views.generate_bill, name="generate_bill"),
    path("bill/<int:bill_id>/", views.bill_detail, name="bill_detail"),
    path("completed-bills/", views.completed_bills, name="completed_bills"),
    path("complete-bill/<int:bill_id>/", views.mark_bill_completed, name="mark_bill_completed"),
    # path("edit-bill/<int:bill_id>/", views.edit_bill, name="edit_bill"),
]