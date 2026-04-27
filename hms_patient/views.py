from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from hms_reception.models import Appointment_details, Patient_details
from hms_admin.models import Doctor_details

from .models import AppointmentOTP
from django.utils import timezone
import secrets
from django.db.models import Max

# Create your views here.
def checkDavailability(request):
    Doctor=Doctor_details.objects.all()
    return render(request,'checkDavailability.html',{'doctors':Doctor})
def generate_token(doctor, date):
    last_token = Appointment_details.objects.filter(DoctorData=doctor, Date=date).count()
    return last_token + 1
from django.utils.safestring import mark_safe
from datetime import datetime, time, timedelta

def calculate_appointment_time(token):
    # Start 9:00 AM
    start_dt = datetime.combine(datetime.today(), time(9, 0))

    total_minutes = (token - 1) * 10

    # Skip 1 PM to 2 PM (9:00 -> 1:00 is 240 minutes)
    if total_minutes >= 240:
        total_minutes += 60

    appt_dt = start_dt + timedelta(minutes=total_minutes)
    return appt_dt.time()
def registerAndBook(request):
    if request.method == 'POST':
        # Patient details
        patient_name = request.POST['name']
        patient_age = request.POST['age']
        patient_gender = request.POST['gender']
        patient_phone = request.POST['phone']
        patient_address = request.POST['address']

        patient_obj = Patient_details.objects.create(
            Patient_name=patient_name,
            Patient_age=patient_age,
            Patient_gender=patient_gender,
            Patient_phone=patient_phone,
            Patient_address=patient_address
        )

        # Appointment details
        doctor_id = request.POST.get("doctor_name")
        date_str = request.POST.get("date")  # "YYYY-MM-DD"

        doctor_obj = get_object_or_404(Doctor_details, id=doctor_id)

        # ✅ convert to date object (NO strptime)
        date_obj = datetime.fromisoformat(date_str).date()

        # Generate token
        token = generate_token(doctor_obj, date_obj)

        # ✅ calculate time
        appt_time = calculate_appointment_time(token)

        # Save appointment with time
        appointment = Appointment_details.objects.create(
            PatientData=patient_obj,
            DoctorData=doctor_obj,
            Date=date_obj,
            Token_number=token,
            Appointment_time=appt_time
        )

        messages.success(
            request,
            mark_safe(
                f"Appointment booked successfully! "
                f"Doctor: <b>{doctor_obj.Doctor_name}</b> | "
                f"Date: <b>{date_obj}</b> | "
                f"Token: <b>{appointment.Token_number}</b> | "
                f"Time: <b>{appt_time.strftime('%I:%M %p')}</b>"
            )
        )

        return redirect('registerAndBook')

    doctors = Doctor_details.objects.all()
    return render(request, 'patientBooking.html', {'doctors': doctors})

# otp validation
# ---------------------------
# STEP 1: Lookup page
# ---------------------------
def patient_manage_lookup(request):
    return render(request, "patient_manage_lookup.html")


# ---------------------------
# STEP 2: Send OTP
# ---------------------------
def patient_send_otp(request):
    if request.method != "POST":
        return redirect("patient_manage_lookup")

    phone_raw = (request.POST.get("phone") or "").strip()
    date_raw = (request.POST.get("date") or "").strip()

    if not phone_raw or not date_raw:
        messages.error(request, "Please enter Phone number and Appointment Date.")
        return redirect("patient_manage_lookup")

    try:
        phone = int(phone_raw)
    except ValueError:
        messages.error(request, "Phone must be a number.")
        return redirect("patient_manage_lookup")

    # Appointment exists check (Phone + Date)
    appts = Appointment_details.objects.select_related("PatientData", "DoctorData").filter(
        Date=date_raw,
        PatientData__Patient_phone=phone
    ).order_by("-id")

    if not appts.exists():
        messages.error(request, "No appointment found for this Phone + Date.")
        return redirect("patient_manage_lookup")

    # ✅ Generate OTP (6-digit)
    otp = str(secrets.randbelow(900000) + 100000)
    AppointmentOTP.objects.create(phone=phone, otp=otp)

    # ✅ TEST MODE (prints in terminal)
    print(f"[OTP] Phone {phone} => OTP: {otp}")

    # Store lookup in session
    request.session["otp_phone"] = phone
    request.session["otp_date"] = date_raw
    request.session["otp_verified"] = False

    messages.success(request, "OTP sent (check SMS).")
    return redirect("patient_verify_otp")


# ---------------------------
# STEP 3: OTP Verify page
# ---------------------------
def patient_verify_otp_page(request):
    phone = request.session.get("otp_phone")
    date_raw = request.session.get("otp_date")

    if not phone or not date_raw:
        messages.error(request, "Session expired. Please try again.")
        return redirect("patient_manage_lookup")

    return render(request, "patient_verify_otp.html", {"phone": phone, "date": date_raw})


def patient_verify_otp(request):
    if request.method != "POST":
        return redirect("patient_manage_lookup")

    phone = request.session.get("otp_phone")
    date_raw = request.session.get("otp_date")
    otp_in = (request.POST.get("otp") or "").strip()

    if not phone or not date_raw:
        messages.error(request, "Session expired. Please try again.")
        return redirect("patient_manage_lookup")

    otp_obj = AppointmentOTP.objects.filter(
        phone=phone,
        otp=otp_in,
        is_used=False
    ).order_by("-created_at").first()

    if (not otp_obj) or (not otp_obj.is_valid()):
        messages.error(request, "Invalid or expired OTP.")
        return redirect("patient_verify_otp")

    otp_obj.is_used = True
    otp_obj.save()

    request.session["otp_verified"] = True
    return redirect("patient_my_appointments")


# ---------------------------
# STEP 4: Show appointments (only after OTP)
# ---------------------------
def patient_my_appointments(request):
    if not request.session.get("otp_verified"):
        messages.error(request, "Please verify OTP first.")
        return redirect("patient_manage_lookup")

    phone = request.session.get("otp_phone")
    date_raw = request.session.get("otp_date")

    appts = Appointment_details.objects.select_related("PatientData", "DoctorData").filter(
        Date=date_raw,
        PatientData__Patient_phone=phone
    ).order_by("-id")

    request.session["patient_allowed_appt_ids"] = list(appts.values_list("id", flat=True))

    return render(request, "patient_my_appointments.html", {"appointments": appts})


# ---------------------------
# CANCEL (secure)
# ---------------------------
def patient_cancel_appointment(request, id):
    allowed = set(request.session.get("patient_allowed_appt_ids", []))
    if id not in allowed:
        messages.error(request, "Not authorized to cancel this appointment.")
        return redirect("patient_manage_lookup")

    appt = get_object_or_404(Appointment_details, id=id)

    if request.method == "POST":
        appt.delete()
        messages.success(request, "Appointment cancelled successfully.")
        return redirect("patient_manage_lookup")

    return render(request, "patient_cancel_confirm.html", {"appointment": appt})


def compute_token_and_time(doctor, date, exclude_appointment_id=None):

    qs = Appointment_details.objects.filter(DoctorData=doctor, Date=date)

    if exclude_appointment_id:
        qs = qs.exclude(id=exclude_appointment_id)

    last_token = qs.aggregate(Max("Token_number"))["Token_number__max"] or 0
    token = last_token + 1

    start_time = time(9, 0)
    slot_minutes = 10

    minutes_from_start = (token - 1) * slot_minutes
    appt_dt = datetime.combine(date, start_time) + timedelta(minutes=minutes_from_start)

    # Lunch break 1–2
    if time(13, 0) <= appt_dt.time() < time(14, 0):
        appt_dt += timedelta(hours=1)

    return token, appt_dt.time()
# ---------------------------
# RESCHEDULE (secure)
# ---------------------------
def patient_reschedule_appointment(request, id):
    appt = get_object_or_404(Appointment_details, id=id)

    # (keep your OTP/session permission checks here)

    if request.method == "POST":
        new_date_str = request.POST.get("date")
        if not new_date_str:
            messages.error(request, "Please select a date.")
            return redirect("patient_reschedule_appointment", id=id)

        new_date = datetime.strptime(new_date_str, "%Y-%m-%d").date()

        # ✅ recompute token + time for the same doctor on the NEW date
        new_token, new_time = compute_token_and_time(
            doctor=appt.DoctorData,
            date=new_date,
            exclude_appointment_id=appt.id
        )

        appt.Date = new_date
        appt.Token_number = new_token
        appt.Appointment_time = new_time
        appt.save()

        messages.success(
            request,
            f"Appointment rescheduled ✅ Token: {new_token}, Time: {new_time.strftime('%H:%M')}"
        )
        return redirect("patient_manage_lookup")  # or your list page

    return render(request, "patient_reschedule.html", {"appointment": appt})