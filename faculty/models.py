from django.db import models
from django.contrib.auth.models import User, Group

# Create your models here.

DEPT = [
    ('AS', 'Applied Science'),
    ('CS', 'Computer Science'),
    ('Civil', 'Civil Engineering'),
    ('EC', 'Electronics and Communication'),
    ('EE', 'Electrical Engineering'),
    ('ME', 'Mechanical Engineering'),
]

DESIGNATION = [
    ('Assistant Professor', 'Assistant Professor'),
    ('Professor', 'Professor'),
    ('HOD', 'HOD'),
]


class Faculty(User):
    user_id = models.BigIntegerField(primary_key=True)
    date_of_birth = models.DateField(blank=True, null=True)
    dept = models.CharField(max_length=10, choices=DEPT)
    phone = models.BigIntegerField(blank=True, null=True)
    designation = models.CharField(max_length=30, choices=DESIGNATION, default='Assistant Professor')
    profile_image = models.ImageField(upload_to='profile', blank=False, null=False)
    REQUIRED_FIELDS = ['email', 'user_id']

    class Meta:
        verbose_name = 'Faculty'
        verbose_name_plural = 'Faculties'

    def save(self, *args, **kwargs):
        if not self.id:
            self.username = str(self.user_id)
        super().save(*args, **kwargs)
