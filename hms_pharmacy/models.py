from django.db import models

class Medicine_inventory(models.Model):
    Medicine_name = models.CharField(max_length=100, unique=True)
    Medicine_price = models.FloatField()
    Stock = models.IntegerField(
        choices=((1, "In Stock"), (0, "Out of Stock")),
        default=1
    )
