from django.contrib import admin
from . import models

# Register your models here.


admin.site.register(models.Subject)

admin.site.register(models.Exam)
admin.site.register(models.QuestionPaper)

admin.site.index_title = 'KIPM - Online Examination Administration'
admin.site.site_title = 'Administration'
admin.site.site_header = 'Admin Page'
