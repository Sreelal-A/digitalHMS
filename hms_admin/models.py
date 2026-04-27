from django.db import models
class Admin_details(models.Model):
  Admin_username = models.CharField(max_length=255)
  Admin_password = models.CharField(max_length=255)

class Doctor_details(models.Model):
  Doctor_name = models.CharField(max_length=255)
  Doctor_username = models.CharField(max_length=255)
  Doctor_password = models.CharField(max_length=255)
  Doctor_phone = models.BigIntegerField()
  Doctor_department = models.CharField(max_length=255,choices=[
                                                              ('Cardiology', 'Cardiology'),
                                                              ('Neurology', 'Neurology'),
                                                              ('Orthopedics', 'Orthopedics'),
                                                              ('Pediatrics', 'Pediatrics'),
                                                              ('Dermatology', 'Dermatology'),
                                                              ('General Medicine', 'General Medicine')])
  availability_status = models.CharField(max_length=255,choices=[('Available', 'Available'),
                                                                 ('Unavailable', 'Unavailable'),
                                                                 ('On Leave', 'On Leave')],
                                                                 default='Available')
            

class Staff_details(models.Model):
  Staff_name = models.CharField(max_length=255)                    
  Staff_username = models.CharField(max_length=255)
  Staff_password = models.CharField(max_length=255)
  Staff_phone_no = models.BigIntegerField()
  Staff_user_type = models.CharField(max_length=255 ,choices=[('Laboratory','Laboratory'),
                                                              ('Receptionist','Receptionist'),
                                                              ('Pharmacy','Pharmacy'),
                                                              ('Billing','Billing')])

