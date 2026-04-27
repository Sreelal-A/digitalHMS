from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse
from django.template import loader
from .models import Admin_details,Staff_details,Doctor_details
from hms_reception.models import Appointment_details
from hms_billing.models import Bill
from hms_admin import views
from django.contrib import messages
def about(request):
    return render(request,'about.html')
def services(request):
    return render(request,'services.html')
def contact(request):
    return render(request,'contact.html')
def adminLogin(request):
    return render(request,'adminLogin.html')

def admin_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = Admin_details.objects.filter(
            Admin_username=username,
            Admin_password=password  # ⚠️ insecure, see note below
        ).first()

        if user:
            request.session['user_id'] = user.id
            messages.success(request, "You have logged in successfully!")
            return redirect('adminHome')
        else:
            messages.error(request,"Invalid username or password")
            return redirect('adminLogin')

    return render(request, 'adminLogin.html')
def Logout(request):
    request.session.flush()
    messages.success(request,"You have logged out successfully!")
    return redirect('hms_home')

def doctor_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = Doctor_details.objects.filter(
            Doctor_username=username,
            Doctor_password=password  
        ).first()

        if user:
            request.session['user_id'] = user.id
            messages.success(request,"You have logged in successfully!")
            return redirect('doctorHome')
        else:
            messages.error(request,"Invalid username or password")
            return redirect('doctorLogin')

    return render(request, 'doctorLogin.html')
 

def staff_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user_type = request.POST.get('usertype')

        user = Staff_details.objects.filter(
            Staff_username=username,
            Staff_password=password,
            Staff_user_type=user_type
        ).first()

        if user: 
            request.session['user_id'] = user.id

            if user.Staff_user_type == 'Receptionist':
                messages.success(request,"You have logged in successfully!")
                return redirect('receptionHome')
            elif user.Staff_user_type == 'Laboratory':
                messages.success(request,"You have logged in successfully!")
                return redirect('laboratoryHome')
            elif user.Staff_user_type == 'Pharmacy':
                messages.success(request,"You have logged in successfully!")
                return redirect('pharmacyHome')
            elif user.Staff_user_type == 'Billing':
                messages.success(request,"You have logged in successfully!")
                return redirect('billingHome')
            else:
                messages.error(request,"Unknown user type")
                return redirect('staffLogin')
        else:
            messages.error(request,"Invalid username or password")
            return redirect('staffLogin')
    return render(request,'staffLogin.html')



def adminHome(request):
    if not request.session.get("user_id"):
        return redirect("admin_login")
    return render(request,'adminHome.html')

def hms_home(request):
    return render(request,'hms_home.html')
def staff_details(request):
    if not request.session.get("user_id"):
        return redirect("admin_login")
    return render(request,'staffDetails.html')
def staff_details_save(request):
    if request.method=="POST":
        staff_name=request.POST['staff_name']
        staff_username=request.POST['username']
        staff_password=request.POST['password']
        staff_phone=request.POST['phone']
        staff_usertype=request.POST['usertype']
        if Staff_details.objects.filter(Staff_username=staff_username).exists():
            messages.error(request,"Username already exists")
            return redirect('staffDetails')
        else:
            data=Staff_details(Staff_name=staff_name,Staff_username=staff_username,Staff_password=staff_password,Staff_phone_no=staff_phone,Staff_user_type=staff_usertype)
            data.save()
            messages.success(request,"Registered Successfully")
            return redirect('staffShow')
    messages.error(request,"Somthing went wrong..." )
    return redirect('staffDetails')
def staffShow(request):
    if not request.session.get("user_id"):
        return redirect("admin_login")
    user_type=request.GET.get('usertype')
    if user_type:
        StaffData=Staff_details.objects.filter(Staff_user_type=user_type)
    else:
        StaffData=Staff_details.objects.all()
    return render(request,'staffShow.html',{'staffs':StaffData})
def staff_delete(request,id):
    Staff_details.objects.filter(id=id).delete()
    return redirect('staffShow')
def staff_edit(request,id):
    staff=get_object_or_404(Staff_details,pk=id)
    if request.method=="POST":
        staff_name=request.POST['staff_name']
        # staff_username=request.POST['username']
        staff_password=request.POST['password']
        staff_phone=request.POST['phone']
        staff_usertype=request.POST['usertype']
        Staff_details.objects.filter(id=id).update(
            Staff_name=staff_name,
            # Staff_username=staff_username,
            Staff_password=staff_password,
            Staff_phone_no=staff_phone,
            Staff_user_type=staff_usertype)
        messages.success(request,"Changes saved")
        return redirect("staffShow")
    return render(request,'staffEdit.html',{'staff':staff})
def staffLogin(request):
    return render(request,'staffLogin.html')
def doctor_details(request):
    if not request.session.get("user_id"):
        return redirect("admin_login")
    return render(request,'doctorDetails.html')
def doctor_details_save(request):
    if request.method=="POST":
        doctor_name=request.POST['name']
        doctor_username=request.POST['username']
        doctor_password=request.POST['password']
        doctor_phone=request.POST['phone']
        doctor_department=request.POST['department']
        # doctor_availability=request.POST['availability_status']
        if Doctor_details.objects.filter(Doctor_username=doctor_username).exists():
            messages.error(request,"Username already exists")
            return redirect('doctorDetails')
        else:
            Doctor=Doctor_details(Doctor_name=doctor_name,
            Doctor_username=doctor_username,
            Doctor_password=doctor_password,
            Doctor_phone=doctor_phone,
            Doctor_department=doctor_department)
            # availability_status=doctor_availability )
            Doctor.save()
            messages.success(request,"Registered Successfully")
            return redirect('doctorFetch')
    return render(request,'doctorDetails.html')
def doctorFetch(request):
    if not request.session.get("user_id"):
        return redirect("admin_login")
    DoctorData=Doctor_details.objects.all()
    return render(request,'doctorFetch.html',{'doctors':DoctorData})
def doctor_delete(request,id):
    Doctor_details.objects.filter(id=id).delete()
    return redirect('doctorFetch')
def doctor_edit(request,id):
    Doctor=get_object_or_404(Doctor_details,id=id)
    if request.method=="POST":
        doctor_name=request.POST['name']
        # doctor_username=request.POST['username']
        doctor_password=request.POST['password']
        doctor_phone=request.POST['phone']
        doctor_department=request.POST['department']
        doctor_availability=request.POST['availability_status']
        Doctor_details.objects.filter(id=id).update(
            Doctor_name=doctor_name,
            # Doctor_username=doctor_username,
            Doctor_password=doctor_password,
            Doctor_phone=doctor_phone,
            Doctor_department=doctor_department,
            availability_status=doctor_availability) 
        messages.success(request,"Changes Saved") 
        return redirect('doctorFetch')
    return render(request,'doctorEdit.html',{'doctor':Doctor})
def doctorLogin(request):
    return render(request,'doctorLogin.html')



def admin_view_appointments(request):
    if not request.session.get("user_id"):
        return redirect("admin_login")
    appointments = Appointment_details.objects.select_related(
        "PatientData", "DoctorData"
    ).order_by("-Date", "Token_number")

    return render(request, "admin_view_appointments.html", {
        "appointments": appointments
    })


def admin_view_completed_bills(request):
    if not request.session.get("user_id"):
        return redirect("admin_login")
    completed_bills = Bill.objects.select_related(
        "appointment",
        "appointment__PatientData",
        "appointment__DoctorData"
    ).filter(status="Completed").order_by("-created_at")

    return render(request, "admin_view_completed_bills.html", {
        "completed_bills": completed_bills
    })
    
