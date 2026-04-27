from django.urls import path
from . import views
urlpatterns = [
    path('receptionHome/',views.R_home,name='receptionHome'),
    path('patientDetails/',views.patientDetails,name='patientDetails'),
    path('patientSave/',views.patientSave,name='patientSave'),
    path('patientFetch/',views.patientFetch,name='patientFetch'),
    path('patientDelete/<int:id>/',views.patientDelete,name='patientDelete'),
    path('patientEdit/<int:id>/',views.patientEdit,name='patientEdit'),
    path('doctor_avail/',views.doctor_avail,name='doctor_avail'),
    path('doctor_availEdit/<int:id>/',views.doctor_availEdit,name='doctor_availEdit'),
    path('bookAppointment/',views.bookAppointment,name='bookAppointment'),
    path('appointmentFetch/',views.appointmentFetch,name='appointmentFetch'),
    path('appointmentEdit/<int:id>/',views.appointmentEdit,name='appointmentEdit'),
    path('appointmentCancel/<int:id>/',views.appointmentCancel,name='appointmentCancel'),
    
    
    
]