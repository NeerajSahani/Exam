"""Exam URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import settings, static
from django.contrib import admin
from django.urls import path, include
from module import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('module.urls', namespace='exam')),
    path('student/', include('student.urls', namespace='student')),
    path('faculty/', include('faculty.urls', namespace='faculty')),
    path('accounts/', include('django.contrib.auth.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'Exam.error_views.page_not_found'
handler500 = 'Exam.error_views.server_error'
handler403 = 'Exam.error_views.permission_denied'
handler400 = 'Exam.error_views.bad_request'
