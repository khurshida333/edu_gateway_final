from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student')
    mobile_no = models.CharField(max_length=12,default='not provided')
    def __str__ (self):
        return f"{self.user.first_name} {self.user.last_name}"