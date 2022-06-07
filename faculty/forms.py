from django.contrib.auth.forms import UserCreationForm
from . import models
from django import forms


class FacultySignupForm(UserCreationForm):
    class Meta:
        model = models.Faculty
        fields = ['user_id', 'first_name', 'last_name', 'email', 'profile_image', 'dept', 'designation', 'phone',
                  'date_of_birth', 'password1', 'password2']
        widgets = {
            'first_name': forms.TextInput(attrs={'type': 'text', 'placeholder': 'First Name', 'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'type': 'text', 'placeholder': 'Last Name', 'class': 'form-control'}),
            'dept': forms.Select(attrs={'class': 'form-control'}),
            'designation': forms.Select(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'placeholder': 'E-mail', 'class': 'form-control'}),
            'profile_image': forms.FileInput(),
            'user_id': forms.NumberInput(attrs={'placeholder': 'University ID', 'class': 'form-control'}),
            'phone': forms.NumberInput(attrs={'placeholder': 'Mobile Number', 'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'vDateField'})
        }
