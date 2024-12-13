from django.contrib.auth.models import User
from django.db import models

class Department(models.Model):
    name = models.CharField(max_length=30, default='Unnamed Department')
    slug = models.CharField(max_length=40, default='')

    def __str__(self):
        return self.name


class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(default='not provided')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='teachers')

    def __str__(self):
        return f"Sir. {self.user.first_name} {self.user.last_name}"


class Course(models.Model):
    title = models.CharField(max_length=100, default='Untitled Course')
    description = models.TextField(default='No description provided')
    duration = models.CharField(max_length=100, default='N/A')
    format = models.CharField(max_length=50, default='online')
    key_features = models.TextField(default='No key features provided')
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='courses')

    def __str__(self):
        return self.title
