from django.contrib import admin
from .import models

# Register your models here
admin.site.register(models.Course)

class DepartmentAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',), }

admin.site.register(models.Department, DepartmentAdmin)
admin.site.register(models.Teacher)




