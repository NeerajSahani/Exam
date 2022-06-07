from django.urls import path
from . import views

app_name = 'student'
urlpatterns = [
    path('dashboard/<int:pk>/', views.StudentDashboard.as_view(), name='dashboard'),
    path('dashboard/student/notifications/', views.NotificationView.as_view(), name='notification'),
    path('signup/', views.Registration.as_view(), name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/<int:pk>/', views.ProfileView.as_view(), name='profile'),
    path('profile/<int:pk>/delete/', views.DeleteStudentProfile.as_view(), name='delete-profile'),
    path('<slug:exam>/<str:username>/result/', views.ResultView.as_view(), name='result-view'),
    path('activate/<str:uidb64>/<slug:token>/', views.activate, name='activate'),
]
