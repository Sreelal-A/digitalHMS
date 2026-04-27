from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Test_master
from hms_doctor.models import Test_details

def laboratoryHome(request):
    if not request.session.get("user_id"):
        return redirect("staff_login")
    return render(request,'laboratoryHome.html')
def manage_tests(request):
    if not request.session.get("user_id"):
        return redirect("staff_login")
    if request.method == "POST":
        name = (request.POST.get("test_name") or "").strip()
        price = (request.POST.get("price") or "").strip()

        if not name or not price:
            messages.error(request, "Please enter both Test name and Price.")
            return redirect("manage_tests")

        try:
            price_val = float(price)
            if price_val < 0:
                raise ValueError
        except ValueError:
            messages.error(request, "Price must be a valid positive number.")
            return redirect("manage_tests")

        if Test_master.objects.filter(Test_name__iexact=name).exists():
            messages.error(request, "This test already exists.")
            return redirect("manage_tests")

        Test_master.objects.create(Test_name=name, Price=price_val)
        messages.success(request, "Test added successfully.")
        return redirect("manage_tests")

    tests = Test_master.objects.all().order_by("Test_name")
    return render(request, "manage_tests.html", {"tests": tests})


def delete_test(request, id):
    if request.method == "POST":
        test = get_object_or_404(Test_master, id=id)
        test.delete()
        messages.success(request, "Test deleted successfully.")
    return redirect("manage_tests")

def test_list(request):
    if not request.session.get("user_id"):
        return redirect("staff_login")
    tests = (
        Test_details.objects
        .select_related("Appointment__PatientData", "Appointment__DoctorData")
        .order_by("-Created_at")
    )
    return render(request, "test_list.html", {"tests": tests})

def test_detail(request, id):
    if not request.session.get("user_id"):
        return redirect("staff_login")
    test = get_object_or_404(
        Test_details.objects.select_related("Appointment__PatientData", "Appointment__DoctorData"),
        id=id
    )

    # ✅ upload report image directly into Test_details (needs model field - see below)
    if request.method == "POST":
        report = request.FILES.get("report_image")
        if report:
            test.Report_image = report
            test.Test_status = "Completed"
            test.save()
            messages.success(request, "Report uploaded and status set to Completed.")
            return redirect("test_list")
        else:
            messages.error(request, "Please select a report image.")

    return render(request, "test_detail.html", {"test": test})

def completed_reports(request):
    if not request.session.get("user_id"):
        return redirect("staff_login")
    tests = (
        Test_details.objects
        .filter(Test_status="Completed")
        .select_related("Appointment__PatientData", "Appointment__DoctorData")
        .order_by("-Created_at"))
    return render(request, "completed_reports.html", {"tests": tests})