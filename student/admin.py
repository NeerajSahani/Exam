from django.contrib import admin
from . import models


# Register your models here.
class StudentAdmin(admin.ModelAdmin):
    list_display = ['username', 'first_name', 'last_name', 'email', 'dept', 'sem', 'is_active']
    list_filter = ['dept', 'sem', 'is_active']


class ResultAdmin(admin.ModelAdmin):
    list_display = ['student', 'exam', 'question_paper']
    list_filter = ['exam', 'question_paper']


admin.site.register(models.Student, StudentAdmin)
admin.site.register(models.Result, ResultAdmin)
admin.site.register(models.Message)
