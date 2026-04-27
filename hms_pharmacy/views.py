from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse
from django.template import loader
from hms_reception import views
from django.contrib import messages
from. models import Medicine_inventory
from hms_doctor.models import Prescription_details,Medicine_details,Test_details
from hms_reception.models import Appointment_details,Patient_details



def pharmacyHome(request):
    if not request.session.get("user_id"):
        return redirect("staff_login")
    return render(request,'pharmacyHome.html')

def addMedicine(request):
    if not request.session.get("user_id"):
        return redirect("staff_login")
    if request.method == "POST":
        name = request.POST.get("name").strip()
        price = request.POST.get("price")
        stock = request.POST.get("stock")

        if Medicine_inventory.objects.filter(Medicine_name__iexact=name).exists():
            messages.error(request, "Medicine already exists")
            return redirect('addMedicine')
        else:
            Medicine_inventory.objects.create(
                Medicine_name=name,
                Medicine_price=float(price),
                Stock=int(stock)
            )
            messages.success(request, "Medicine added successfully")
            return redirect('addMedicine')

    medicines = Medicine_inventory.objects.all().order_by("Medicine_name")

    return render(request, "addMedicine.html", {
        "medicines": medicines
    })
def prescriptionFP(request):
    if not request.session.get("user_id"):
        return redirect("staff_login")
    prescriptions = Prescription_details.objects.all()
    return render(request, 'prescriptionFP.html', {
        'prescriptions': prescriptions
    })
def view_prescription(request, id):
    if not request.session.get("user_id"):
        return redirect("staff_login")
    prescription = get_object_or_404(Prescription_details, id=id)

    appointment = prescription.Appointment
    tests = appointment.tests.all()  # because related_name="tests"

    return render(request, 'view_prescription.html', {
        'prescription': prescription,
        'appointment': appointment,
        'tests': tests,
    })
def updateMedicine(request, id):
    if not request.session.get("user_id"):
        return redirect("staff_login")
    if request.method == "POST":
        med = get_object_or_404(Medicine_inventory, id=id)
        stock_value = request.POST.get("stock")

        med.Stock = int(stock_value)
        med.save()

        messages.success(request, f"{med.Medicine_name} stock updated successfully!")
        return redirect("addMedicine")
    

def lab_reports_pharmacy(request):
    if not request.session.get("user_id"):
        return redirect("staff_login")
    tests = (
        Test_details.objects
        .filter(Test_status="Completed")
        .select_related("Appointment__PatientData", "Appointment__DoctorData")
        .order_by("-Created_at")
    )
    return render(request, "lab_reports_pharmacy.html", {"tests": tests})