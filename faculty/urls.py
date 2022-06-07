from django.urls import path
from . import views

app_name = 'faculty'
urlpatterns = [
    path('signup', views.Registration.as_view(), name='signup'),
    path('login', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/<int:pk>/', views.ProfileView.as_view(), name='profile'),
    path('profile/<int:pk>/delete/', views.DeleteFacultyProfile.as_view(), name='delete-profile'),
    path('activate/<int:pk>/', views.activate, name='profile-activate'),
    path('dashboard/<int:pk>/', views.FacultyDashboard.as_view(), name='dashboard'),
    path('ajax-query', views.ajax_query, name='ajax-query')
]
