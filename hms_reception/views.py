from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse
from django.template import loader
from .models import Patient_details
from .models import Appointment_details
from hms_admin.models import Doctor_details
from django.contrib import messages
from datetime import datetime, time, timedelta
def R_home(request):
    if not request.session.get("user_id"):
        return redirect("staff_login")
    return render(request,'receptionHome.html')
def patientDetails(request):
    if not request.session.get("user_id"):
        return redirect("staff_login")
    return render(request,'patientDetails.html')
def patientSave(request):
    if request.method=='POST':
        patient_name=request.POST['name']
        patient_age=int(request.POST['age'])
        patient_gender=request.POST['gender']
        patient_phone=request.POST['phone']
        patient_address=request.POST['address']
        pdata=Patient_details(Patient_name=patient_name,
                              Patient_age=patient_age,
                              Patient_gender=patient_gender,
                              Patient_phone=patient_phone,
                              Patient_address=patient_address)
        pdata.save()
        messages.success(request,"Registered Successfully")
        return redirect('patientFetch') 
    messages.error(request,"Something went wrong")    
    return redirect('patientDetails')
def patientFetch(request):
    if not request.session.get("user_id"):
        return redirect("staff_login")
    PatientData=Patient_details.objects.all()
    return render(request,'patientFetch.html',{'patients':PatientData})
def patientDelete(request,id):
    Patient_details.objects.filter(id=id).delete()
    return redirect('patientFetch')
def patientEdit(request,id):
    Patient=get_object_or_404(Patient_details,id=id)
    if request.method=='POST':
        patient_name=request.POST['name']
        patient_age=request.POST['age']
        patient_gender=request.POST['gender']
        patient_phone=request.POST['phone']
        patient_address=request.POST['address']
        Patient_details.objects.filter(id=id).update(
            Patient_name=patient_name,
            Patient_age=patient_age,
            Patient_gender=patient_gender,
            Patient_phone=patient_phone,
            Patient_address=patient_address,)
        messages.success(request,"Changes saved")
        return redirect('patientFetch')
    return render(request,'patientEdit.html', { 'patient':Patient})
def doctor_avail(request):
    if not request.session.get("user_id"):
        return redirect("staff_login")
    Doctor=Doctor_details.objects.all()
    return render(request,'doctor_avail.html',{'doctors':Doctor})
def doctor_availEdit(request,id):
    Doctor=get_object_or_404(Doctor_details,id=id)
    if request.method=="POST":
        doctor_availability=request.POST['availability_status']
        Doctor_details.objects.filter(id=id).update(availability_status=doctor_availability) 
        messages.success(request,"Changes saved")
        return redirect('doctor_avail')
    return render(request,'doctor_availEdit.html',{'doctor':Doctor})
def generate_token(doctor, date):
    last_token = Appointment_details.objects.filter(DoctorData=doctor, Date=date).count()
    return last_token + 1
def bookAppointment(request):
    if not request.session.get("user_id"):
        return redirect("staff_login")
    patients = Patient_details.objects.all()
    doctors = Doctor_details.objects.all()

    if request.method == "POST":
        patient_name = request.POST.get("patient_name")
        doctor_name = request.POST.get("doctor_name")
        date = request.POST.get("date")

        patient_obj = get_object_or_404(Patient_details, id=patient_name)
        doctor_obj = get_object_or_404(Doctor_details, id=doctor_name)

        token = generate_token(doctor_obj, date)
        appt_time = calculate_appointment_time(token)

        Appointment_details.objects.create(PatientData=patient_obj,DoctorData=doctor_obj,Date=date,Token_number=token,Appointment_time=appt_time)
        messages.success(request,"Booked successfully.")
        return redirect('appointmentFetch')
    return render(request, 'appointment.html', {
        'patients': patients,
        'doctors': doctors
    })

def calculate_appointment_time(token):
    start_dt = datetime.combine(datetime.today(), time(9, 0))
    total_minutes = (token - 1) * 10
    appt_dt = start_dt + timedelta(minutes=total_minutes)

    # Skip 1 PM to 2 PM lunch break
    if time(13, 0) <= appt_dt.time() < time(14, 0):
        appt_dt += timedelta(hours=1)

    return appt_dt.time()
    return appt_dt.time()

def appointmentFetch(request):
    if not request.session.get("user_id"):
        return redirect("staff_login")
    appointments = Appointment_details.objects.all().order_by("Date", "Token_number")
    return render(request, "appointmentFetch.html", {"appointments": appointments})
def appointmentEdit(request, id):
    appointment = get_object_or_404(Appointment_details, id=id)

    if request.method == "POST":
        patient_id = request.POST.get("patient_name")
        doctor_id = request.POST.get("doctor_name")
        date = request.POST.get("date")

        patient_obj = get_object_or_404(Patient_details, id=patient_id)
        doctor_obj = get_object_or_404(Doctor_details, id=doctor_id)

        token = generate_token(doctor_obj, date)
        appt_time = calculate_appointment_time(token)   # NEW

        # Update appointment
        appointment.PatientData = patient_obj
        appointment.DoctorData = doctor_obj
        appointment.Date = date
        appointment.Token_number = token
        appointment.Appointment_time = appt_time        # NEW
        appointment.save()

        messages.success(request, "Changed successfully.")
        return redirect('appointmentFetch')

    patients = Patient_details.objects.all()
    doctors = Doctor_details.objects.all()

    return render(request, 'appointmentEdit.html', {
        'appointment': appointment,
        'patients': patients,
        'doctors': doctors
    })
def appointmentCancel(request,id):
    if request.method == "POST":
        Appointment_details.objects.filter(id=id).delete()
        messages.error(request,"Appointment canceled!")
    return redirect('appointmentFetch')