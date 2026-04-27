from decimal import Decimal
from django.db import models
from django.utils import timezone

from hms_reception.models import Appointment_details
from hms_laboratory.models import Test_master
from hms_pharmacy.models import Medicine_inventory


class Bill(models.Model):
    appointment = models.OneToOneField(Appointment_details, on_delete=models.CASCADE, related_name="bill")
    doctor_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(
        max_length=15,
        choices=[('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
    ],
        default='PENDING'
    )

    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Bill #{self.id} - Appt {self.appointment.id}"


class BillTestItem(models.Model):
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE, related_name="test_items")
    test = models.ForeignKey(Test_master, on_delete=models.PROTECT)
    test_name_snapshot = models.CharField(max_length=255)
    test_price_snapshot = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.test_name_snapshot}"


class BillMedicineItem(models.Model):
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE, related_name="medicine_items")
    medicine = models.ForeignKey(Medicine_inventory, on_delete=models.PROTECT, null=True, blank=True)

    medicine_name_snapshot = models.CharField(max_length=255)
    price_per_piece_snapshot = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    duration_days = models.PositiveIntegerField(default=0)
    times_per_day = models.PositiveIntegerField(default=0)

    quantity = models.PositiveIntegerField(default=0)
    total_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.medicine_name_snapshot}"