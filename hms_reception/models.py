from django.db import models
from hms_admin.models import Doctor_details

from django.utils import timezone


class Patient_details(models.Model):
    Patient_name=models.CharField(max_length=255)
    Patient_age=models.IntegerField()                      
    Patient_gender=models.CharField(max_length=255,choices=[('Male','Male'),
                                                            ('Female','Female'),
                                                            ('Others','Others')])
    Patient_phone=models.BigIntegerField()
    Patient_address=models.CharField(max_length=255)

class Appointment_details(models.Model):
    PatientData=models.ForeignKey(Patient_details, on_delete=models.CASCADE)
    DoctorData=models.ForeignKey(Doctor_details, on_delete=models.CASCADE)
    Date=models.DateField()
    Token_number=models.IntegerField()
    Appointment_time = models.TimeField(null=True, blank=True)
    Prescription_status = models.CharField(max_length=20, choices=[("Pending", "Pending"),
                                                      ("Complete", "Complete")],
                                                      default="Pending")
    Created_at = models.DateTimeField(default=timezone.now)
