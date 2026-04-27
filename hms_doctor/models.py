from django.db import models
from hms_reception.models import Appointment_details
from hms_pharmacy.models import Medicine_inventory

class Prescription_details(models.Model):
    Appointment = models.OneToOneField(Appointment_details, on_delete=models.CASCADE, related_name="prescriptions")
    Duration = models.IntegerField()  # in days
    Diagnosis=models.CharField(max_length=255,null=True)
    Notes = models.TextField(blank=True, null=True)
    Created_at = models.DateTimeField(auto_now_add=True)

class Medicine_details(models.Model):
    Prescription = models.ForeignKey(Prescription_details, on_delete=models.CASCADE, related_name="medicines")
    Medicine = models.ForeignKey(Medicine_inventory, on_delete=models.PROTECT,null=True,blank=True)

    # Separate dosage fields
    Morning = models.IntegerField(default=0)   # 0 or 1
    Afternoon = models.IntegerField(default=0) # 0 or 1
    Night = models.IntegerField(default=0)     # 0 or 1

    Instructions = models.CharField(
        max_length=255,
        choices=[
            ("After Food", "After Food"),
            ("Before Food", "Before Food"),
            ("Morning", "Morning"),
            ("Night", "Night"),
        ],
        blank=True,
        null=True
    )

class Test_details(models.Model):
    Appointment = models.ForeignKey(Appointment_details, on_delete=models.CASCADE, related_name="tests")
    Test_name = models.CharField(max_length=255)
    Notes = models.TextField(blank=True, null=True)
    Test_status = models.CharField(
        max_length=20,
        choices=[("Assigned", "Assigned"), ("Completed", "Completed")],
        default="Assigned")
    Report_image = models.ImageField(upload_to="lab_reports/", null=True, blank=True)
    Created_at = models.DateTimeField(auto_now_add=True)


