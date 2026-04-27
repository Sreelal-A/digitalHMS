from django.urls import path
from . import views
urlpatterns = [
    path('about/',views.about,name='about'),
    path('services/',views.services,name='services'),
    path('contact/',views.contact,name='contact'),
    path('adminLogin/',views.adminLogin,name='adminLogin'),
    path('admin_login/',views.admin_login,name='admin_login'),
    path('staff_login/',views.staff_login,name='staff_login'),
    path('adminHome/',views.adminHome,name='adminHome'),
    path('',views.hms_home,name='hms_home'),
    path('staffDetails/',views.staff_details,name='staffDetails'),
    path('save/',views.staff_details_save,name='staff_save'),
    path('staffShow/',views.staffShow,name='staffShow'),
    path('staff_delete/<int:id>/',views.staff_delete,name='staff_delete'),
    path('staff_edit/<int:id>/',views.staff_edit,name='staff_edit'),
    path('staffLogin/',views.staffLogin,name='staffLogin'),
    path('doctorDetails/',views.doctor_details,name='doctorDetails'),
    path('doctor_save/',views.doctor_details_save,name='doctor_save'),
    path('doctorFetch/',views.doctorFetch,name='doctorFetch'),
    path('doctor_delete/<int:id>/',views.doctor_delete,name='doctor_delete'),
    path('doctor_edit/<int:id>/',views.doctor_edit,name='doctor_edit'),
    path('doctorLogin/',views.doctorLogin,name='doctorLogin'),
    path('doctor_login/',views.doctor_login,name='doctor_login'),
    path('Logout/',views.Logout,name='Logout'),


    path("appointments/", views.admin_view_appointments, name="admin_view_appointments"),
    path("completed-bills/", views.admin_view_completed_bills, name="admin_view_completed_bills"),
    
]