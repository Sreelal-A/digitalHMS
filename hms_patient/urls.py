from django.urls import path
from . import views
urlpatterns = [
    path('checkDavailability/',views.checkDavailability,name='checkDavailability'),
    path('registerAndBook/', views.registerAndBook, name="registerAndBook"),


     # ✅ Manage appointment with OTP
    path('manage/', views.patient_manage_lookup, name='patient_manage_lookup'),
    path('manage/send-otp/', views.patient_send_otp, name='patient_send_otp'),
    path('manage/verify/', views.patient_verify_otp_page, name='patient_verify_otp'),
    path('manage/verify/submit/', views.patient_verify_otp, name='patient_verify_otp_submit'),
    path('manage/appointments/', views.patient_my_appointments, name='patient_my_appointments'),

    path('manage/appointment/<int:id>/cancel/', views.patient_cancel_appointment, name='patient_cancel_appointment'),
    path('manage/appointment/<int:id>/reschedule/', views.patient_reschedule_appointment, name='patient_reschedule_appointment'),
    

]