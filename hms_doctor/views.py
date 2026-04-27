from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse
from django.template import loader
from .models import Prescription_details,Medicine_details,Test_details
from hms_reception.models import Appointment_details,Patient_details
from hms_pharmacy.models import Medicine_inventory
from hms_laboratory.models import Test_master
from hms_admin.models import Doctor_details
from django.contrib import messages

import json
from django.http import JsonResponse


def doctorHome(request):
    if not request.session.get("user_id"):
        return redirect("doctor_login")
    return render(request,'doctorHome.html')
def appointmentFD(request):
    if not request.session.get("user_id"):
        return redirect("doctor_login")

    doctor_id = request.session.get("user_id")
    doctor = get_object_or_404(Doctor_details, id=doctor_id)

    appointments = Appointment_details.objects.filter(
        DoctorData=doctor
    ).order_by("Date", "Token_number")

    return render(request, "appointmentFD.html", {
        "doctor": doctor,
        "appointments": appointments
    })

#priscription
def create_prescription(request, id):
    appointment = get_object_or_404(Appointment_details, id=id)
    medicines_master = Medicine_inventory.objects.filter(Stock=1)
    # past_prescription
    patient = appointment.PatientData
    previous_prescriptions = Prescription_details.objects.filter(
    Appointment__PatientData=patient).order_by("-Created_at")
    if request.method == "POST":
        prescription = Prescription_details.objects.create(
            Appointment=appointment,
            Diagnosis=request.POST.get("diagnosis"),
            Duration=int(request.POST.get("duration") or 0),
            Notes=request.POST.get("notes")
        )

        medicines = request.POST.getlist("medicine[]")
        mornings = request.POST.getlist("morning[]")
        afternoons = request.POST.getlist("afternoon[]")
        nights = request.POST.getlist("night[]")
        instructions = request.POST.getlist("instructions[]")

        for i in range(len(medicines)):
            if medicines[i]:
                med = get_object_or_404(Medicine_inventory, id=medicines[i])

                Medicine_details.objects.create(
                    Prescription=prescription,
                    Medicine=med,
                    Morning=int(mornings[i]) if i < len(mornings) else 0,
                    Afternoon=int(afternoons[i]) if i < len(afternoons) else 0,
                    Night=int(nights[i]) if i < len(nights) else 0,
                    Instructions=instructions[i] if i < len(instructions) else None
                )

         
        appointment.Prescription_status = "Complete"
        appointment.save()


        messages.success(request, "Prescription saved successfully")
        return redirect('appointmentFD')

    return render(request, "create_prescription.html", {"appointment": appointment,
                                                        "medicines_master": medicines_master,
                                                        "previous_prescriptions": previous_prescriptions})

def prescriptionFetch(request, id):
    # id = appointment id
    appointment = get_object_or_404(Appointment_details, id=id)

    # fetch prescription for this appointment
    prescription = Prescription_details.objects.filter(Appointment=appointment).first()

    if not prescription:
        messages.error(request, "Prescription not created yet.")
        return redirect("appointmentFD")  # or redirect back to appointment list

    tests = appointment.tests.all()

    return render(
        request,
        "prescriptionFetch.html",
        {
            "prescription": prescription,
            "appointment": appointment,
            "tests": tests,
        }
    )

def addTest(request, id):
    appointment = get_object_or_404(Appointment_details, id=id)
    test_master_list = Test_master.objects.all().order_by("Test_name")

    if request.method == "POST":
        tests = request.POST.getlist("tests[]")
        notes = request.POST.get("notes")

        for t in tests:
            Test_details.objects.create(
                Appointment=appointment,
                Test_name=t,
                Notes=notes,
                Test_status="Assigned"
            )

        messages.success(request, "Tests assigned successfully.")
        return redirect("create_prescription", id=id)

    return render(request, "addTest.html", {
        "appointment": appointment,
        "test_master_list": test_master_list
    })
def PTedit(request, id):
    prescription = get_object_or_404(Prescription_details, id=id)
    appointment = prescription.Appointment

    # Existing Medicines
    existing_meds = Medicine_details.objects.filter(
        Prescription=prescription
    ).select_related("Medicine")

    # Existing Tests
    existing_tests = Test_details.objects.filter(
        Appointment=appointment
    ).order_by("-Created_at")

    # Masters
    medicines_master = Medicine_inventory.objects.filter(Stock=1).order_by("Medicine_name")
    tests_master = (
        Test_details.objects.values_list("Test_name", flat=True)
        .distinct()
        .order_by("Test_name")
    )

    existing_test_names = list(existing_tests.values_list("Test_name", flat=True))

    if request.method == "POST":

        # --------------------------------------------------
        # 1️⃣ Update Prescription Header
        # --------------------------------------------------
        prescription.Diagnosis = (request.POST.get("diagnosis") or "").strip()
        prescription.Duration = int(request.POST.get("duration") or 0)
        prescription.Notes = (request.POST.get("notes") or "").strip()
        prescription.save()

        # --------------------------------------------------
        # 2️⃣ Delete Medicines (Removed in UI)
        # --------------------------------------------------
        delete_ids = request.POST.getlist("delete_medicine_ids[]")

        if delete_ids:
            Medicine_details.objects.filter(
                Prescription=prescription,
                id__in=delete_ids
            ).delete()

        # --------------------------------------------------
        # 3️⃣ Update / Create Medicines
        # --------------------------------------------------
        detail_ids = request.POST.getlist("medicine_detail_id[]")
        med_ids = request.POST.getlist("medicine[]")
        mornings = request.POST.getlist("morning[]")
        afternoons = request.POST.getlist("afternoon[]")
        nights = request.POST.getlist("night[]")
        instructions = request.POST.getlist("instructions[]")

        row_count = len(med_ids)

        for i in range(row_count):

            med_id = (med_ids[i] or "").strip()
            detail_id = (detail_ids[i] or "").strip()

            if not med_id:
                continue

            morning = int(mornings[i] or 0)
            afternoon = int(afternoons[i] or 0)
            night = int(nights[i] or 0)
            instruction = (instructions[i] or "").strip() or None

            if detail_id:
                # Update existing medicine
                md = Medicine_details.objects.filter(
                    Prescription=prescription,
                    id=detail_id
                ).first()

                if md:
                    md.Medicine_id = med_id
                    md.Morning = morning
                    md.Afternoon = afternoon
                    md.Night = night
                    md.Instructions = instruction
                    md.save()
            else:
                # Create new medicine
                Medicine_details.objects.create(
                    Prescription=prescription,
                    Medicine_id=med_id,
                    Morning=morning,
                    Afternoon=afternoon,
                    Night=night,
                    Instructions=instruction
                )

        # --------------------------------------------------
        # 4️⃣ Sync Tests (Tag-based like addTest)
        # --------------------------------------------------
        selected_tests = request.POST.getlist("tests[]")
        selected_tests = [t.strip() for t in selected_tests if t.strip()]

        selected_set = set(selected_tests)
        existing_set = set(existing_test_names)

        # ❌ Remove unselected tests
        tests_to_delete = existing_set - selected_set
        if tests_to_delete:
            Test_details.objects.filter(
                Appointment=appointment,
                Test_name__in=tests_to_delete
            ).delete()

        # ➕ Add new tests
        new_tests = selected_set - existing_set
        tests_notes = (request.POST.get("tests_notes") or "").strip()

        for tname in new_tests:
            Test_details.objects.create(
                Appointment=appointment,
                Test_name=tname,
                Notes=tests_notes,
                Test_status="Assigned"
            )

        messages.success(request, "Prescription updated successfully ✅")
        return redirect("prescriptionFetch", id=appointment.id)

    return render(request, "PTedit.html", {
        "prescription": prescription,
        "appointment": appointment,
        "existing_meds": existing_meds,
        "existing_tests": existing_tests,
        "medicines_master": medicines_master,
        "tests_master": tests_master,
        "existing_tests_json": json.dumps(existing_test_names),
    })
# AJAX
def medicine_search(request):
    q = request.GET.get("q", "")
    medicines = Medicine_inventory.objects.filter(Medicine_name__icontains=q)[:20]
    results = [{"id": m.id, "text": m.Medicine_name} for m in medicines]
    return JsonResponse({"results": results})

def test_search(request):
    q = (request.GET.get("q") or "").strip()

    qs = Test_master.objects.all()
    if q:
        qs = qs.filter(Test_name__icontains=q)

    tests = qs.order_by("Test_name")[:25]

    results = [
        {"id": t.id, "text": t.Test_name, "price": str(t.Price)}
        for t in tests
    ]
    return JsonResponse({"results": results})
#    --------------------------------------------------------------------------------------------------------------

def patient_history(request, id):
    appointment = get_object_or_404(Appointment_details, id=id)
    patient = appointment.PatientData

    prescriptions = (
        Prescription_details.objects
        .select_related("Appointment", "Appointment__DoctorData")
        .filter(Appointment__PatientData=patient)
        .order_by("-Appointment__Date", "-id")
    )

    return render(request, "patient_history_partial.html", {
        "patient": patient,
        "prescriptions": prescriptions,
    })

def doctor_completed_reports(request):
    if not request.session.get("user_id"):
        return redirect("doctor_login")
    search = (request.GET.get("search") or "").strip()

    tests = (
        Test_details.objects
        .filter(Test_status="Completed")
        .select_related("Appointment__PatientData", "Appointment__DoctorData")
        .order_by("-Created_at")
    )

    # ✅ filter by patient name
    if search:
        tests = tests.filter(
            Appointment__PatientData__Patient_name__icontains=search
        )

    return render(request, "doctor_completed_reports.html", {
        "tests": tests,
        "search": search
    })


