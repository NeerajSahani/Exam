from django.contrib import admin
from . import models


# Register your models here.
class FacultyAdmin(admin.ModelAdmin):
    list_display = ['username', 'first_name', 'last_name', 'email', 'dept', 'is_active']


admin.site.register(models.Faculty, FacultyAdmin)
