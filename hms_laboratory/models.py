from django.db import models

# Create your models here.
class Test_master(models.Model):
    Test_name = models.CharField(max_length=255, unique=True)
    Price = models.DecimalField(max_digits=10, decimal_places=2)
    Created_at = models.DateTimeField(auto_now_add=True)