from django.db import models
from django.utils import timezone

class AppointmentOTP(models.Model):
    phone = models.BigIntegerField()
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def is_valid(self):
        # valid for 5 minutes
        return (timezone.now() - self.created_at).total_seconds() <= 300 and not self.is_used