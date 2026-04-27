from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from hms_reception.models import Appointment_details
from hms_doctor.models import Prescription_details, Medicine_details, Test_details
from hms_laboratory.models import Test_master
from hms_pharmacy.models import Medicine_inventory

from .models import Bill, BillTestItem, BillMedicineItem


def billingHome(request):
    if not request.session.get("user_id"):
        return redirect("staff_login")
    return render(request, "billingHome.html")


def billing_patient_list(request):
    if not request.session.get("user_id"):
        return redirect("staff_login")
    appointments = Appointment_details.objects.select_related(
        "PatientData",
        "DoctorData"
    ).filter(
        Prescription_status="Complete"
    ).order_by("-Created_at")

    for a in appointments:
        a.bill_obj = Bill.objects.filter(appointment=a).first()

    return render(request, "billing_patient_list.html", {
        "appointments": appointments
    })


def generate_bill(request, appointment_id):
    if not request.session.get("user_id"):
        return redirect("staff_login")
    appointment = get_object_or_404(
        Appointment_details.objects.select_related("PatientData", "DoctorData"),
        id=appointment_id
    )

    prescription = Prescription_details.objects.filter(Appointment=appointment).order_by("-Created_at").first()
    assigned_tests = Test_details.objects.filter(Appointment=appointment).order_by("-Created_at")

    prescription_medicines = []
    if prescription:
        prescription_medicines = Medicine_details.objects.select_related("Medicine").filter(Prescription=prescription)

    # ---------- Build Preview Lines ----------
    test_lines = []
    test_total = Decimal("0.00")

    for t in assigned_tests:
        master = Test_master.objects.filter(Test_name__iexact=t.Test_name.strip()).first()
        price = Decimal("0.00")
        if master:
            price = Decimal(str(master.Price))

        test_lines.append({
            "assigned_id": t.id,  # ✅ used for checkbox value
            "name": t.Test_name,
            "price": price,
            "found_in_master": bool(master),
            "master_id": master.id if master else None,
        })
        test_total += price

    med_lines = []
    med_total = Decimal("0.00")

    if prescription:
        duration = int(prescription.Duration or 0)

        for m in prescription_medicines:
            if not m.Medicine:
                continue

            times_per_day = int(m.Morning or 0) + int(m.Afternoon or 0) + int(m.Night or 0)
            qty = duration * times_per_day

            price_per_piece = Decimal(str(m.Medicine.Medicine_price))
            line_total = price_per_piece * Decimal(qty)

            med_lines.append({
                "presc_med_id": m.id,  # ✅ used for checkbox value
                "name": m.Medicine.Medicine_name,
                "price_per_piece": price_per_piece,
                "duration": duration,
                "times_per_day": times_per_day,
                "quantity": qty,
                "total": line_total,
                "medicine_id": m.Medicine.id
            })
            med_total += line_total

    # ---------- POST: Save only selected items ----------
    if request.method == "POST":
        # prevent duplicates
        if Bill.objects.filter(appointment=appointment).exists():
            messages.error(request, "Bill already generated for this appointment.")
            return redirect("billing_patient_list")

        # Doctor fee
        doctor_fee_raw = request.POST.get("doctor_fee", "0") or "0"
        try:
            doctor_fee = Decimal(doctor_fee_raw)
        except:
            doctor_fee = Decimal("0.00")

        # checkbox selections
        def to_int_set(values):
            s = set()
            for v in values:
                try:
                    s.add(int(v))
                except:
                    pass
            return s

        selected_test_ids = to_int_set(request.POST.getlist("include_tests"))
        selected_med_ids = to_int_set(request.POST.getlist("include_meds"))

        bill = Bill.objects.create(
            appointment=appointment,
            doctor_fee=doctor_fee,
            total_amount=Decimal("0.00")
        )

        # Save selected tests
        for tl in test_lines:
            if tl["assigned_id"] not in selected_test_ids:
                continue  # ✅ ignored

            if not tl["master_id"]:
                continue  # no master price, skip

            test_obj = Test_master.objects.get(id=tl["master_id"])
            BillTestItem.objects.create(
                bill=bill,
                test=test_obj,
                test_name_snapshot=tl["name"],
                test_price_snapshot=tl["price"]
            )

        # Save selected medicines
        for ml in med_lines:
            if ml["presc_med_id"] not in selected_med_ids:
                continue  # ✅ ignored

            med_obj = Medicine_inventory.objects.get(id=ml["medicine_id"])
            BillMedicineItem.objects.create(
                bill=bill,
                medicine=med_obj,
                medicine_name_snapshot=ml["name"],
                price_per_piece_snapshot=ml["price_per_piece"],
                duration_days=ml["duration"],
                times_per_day=ml["times_per_day"],
                quantity=ml["quantity"],
                total_price=ml["total"]
            )

        # final total from DB (backend truth)
        total = bill.doctor_fee
        total += sum((x.test_price_snapshot for x in bill.test_items.all()), Decimal("0.00"))
        total += sum((x.total_price for x in bill.medicine_items.all()), Decimal("0.00"))

        bill.total_amount = total
        bill.save()

        messages.success(request, "Bill generated successfully ✅")
        return redirect("bill_detail", bill_id=bill.id)

    context = {
        "appointment": appointment,
        "prescription": prescription,
        "test_lines": test_lines,
        "med_lines": med_lines,
        "test_total": test_total,
        "med_total": med_total,
        "grand_preview_total": (test_total + med_total),
    }
    return render(request, "generate_bill.html", context)


def bill_detail(request, bill_id):
    if not request.session.get("user_id"):
        return redirect("staff_login")
    bill = get_object_or_404(
        Bill.objects.select_related("appointment__PatientData", "appointment__DoctorData"),
        id=bill_id
    )
    return render(request, "bill_detail.html", {"bill": bill})


def completed_bills(request):
    if not request.session.get("user_id"):
        return redirect("staff_login")
    bills = Bill.objects.select_related(
        "appointment__PatientData",
        "appointment__DoctorData"
    ).order_by("-created_at")

    return render(request, "completed_bills.html", {"bills": bills})

def mark_bill_completed(request, bill_id):
    if not request.session.get("user_id"):
        return redirect("staff_login")
    bill = get_object_or_404(Bill, id=bill_id)

    bill.status = 'COMPLETED'
    bill.save()

    messages.success(request, "Bill marked as completed ✅")
    return redirect('bill_detail', bill_id=bill.id)
# def edit_bill(request, bill_id):
#     bill = get_object_or_404(Bill, id=bill_id)

#     # Optional protection: don't edit completed bills
#     if getattr(bill, "status", "PENDING") == "COMPLETED":
#         messages.error(request, "Completed bills cannot be edited.")
#         return redirect("bill_detail", bill_id=bill.id)

#     # ✅ IDs already included in this bill (for checkbox checked state)
#     selected_test_ids = set(bill.test_items.values_list("test_id", flat=True))
#     selected_med_ids = set(bill.medicine_items.values_list("medicine_id", flat=True))

#     tests = Test_master.objects.all().order_by("Test_name")
#     medicines = Medicine_inventory.objects.all().order_by("Medicine_name")

#     if request.method == "POST":
#         # Doctor fee
#         doctor_fee_raw = request.POST.get("doctor_fee", "0") or "0"
#         try:
#             bill.doctor_fee = Decimal(doctor_fee_raw)
#         except:
#             bill.doctor_fee = Decimal("0.00")
#         bill.save()

#         # Selected from form
#         posted_test_ids = request.POST.getlist("include_tests")
#         posted_med_ids = request.POST.getlist("include_meds")

#         # Clear old items
#         BillTestItem.objects.filter(bill=bill).delete()
#         BillMedicineItem.objects.filter(bill=bill).delete()

#         # Save selected tests
#         for tid in posted_test_ids:
#             try:
#                 t = Test_master.objects.get(id=int(tid))
#             except:
#                 continue
#             BillTestItem.objects.create(
#                 bill=bill,
#                 test=t,
#                 test_name_snapshot=t.Test_name,
#                 test_price_snapshot=Decimal(str(t.Price))
#             )

#         # Save selected medicines
#         # NOTE: This keeps existing quantity/total logic SIMPLE.
#         # If you want editing of duration/times/day/qty, tell me & I’ll add it.
#         for mid in posted_med_ids:
#             try:
#                 m = Medicine_inventory.objects.get(id=int(mid))
#             except:
#                 continue

#             price = Decimal(str(m.Medicine_price))
#             BillMedicineItem.objects.create(
#                 bill=bill,
#                 medicine=m,
#                 medicine_name_snapshot=m.Medicine_name,
#                 price_per_piece_snapshot=price,
#                 duration_days=1,
#                 times_per_day=1,
#                 quantity=1,
#                 total_price=price
#             )

#         # Recalculate total
#         total = bill.doctor_fee
#         total += sum((x.test_price_snapshot for x in bill.test_items.all()), Decimal("0.00"))
#         total += sum((x.total_price for x in bill.medicine_items.all()), Decimal("0.00"))

#         bill.total_amount = total
#         bill.save()

#         messages.success(request, "Bill updated successfully ✅")
#         return redirect("bill_detail", bill_id=bill.id)

#     return render(request, "edit_bill.html", {
#         "bill": bill,
#         "tests": tests,
#         "medicines": medicines,
#         "selected_test_ids": selected_test_ids,
#         "selected_med_ids": selected_med_ids,
#     })