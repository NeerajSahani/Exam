from multiprocessing.context import _force_start_method
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.urls import reverse
from module.models import Subject, Exam
from . import forms
from . import models
from django.views import generic
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail, mail_admins
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from .tokens import account_activation_token
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.conf.urls.static import settings


@method_decorator(never_cache, 'dispatch')
class Registration(generic.CreateView, SuccessMessageMixin):
    form_class = forms.StudentSignupForm
    context_object_name = 'form'
    template_name = 'student/signup.html'
    success_message = "Activation link is sent to your Email\nActivate Account before Login"

    def get_success_url(self):
        return reverse('student:login')

    def form_valid(self, form):
        form.instance.is_active = False
        mail_subject = 'Activate your account'
        message = render_to_string('student/confirmation_email.html', {
            'user': str(form.instance.user_id),
            'domain': get_current_site(self.request).domain,
            'uid': urlsafe_base64_encode(force_bytes(form.instance.user_id)),
            'token': account_activation_token.make_token(form.instance),
        })
        to_email = form.cleaned_data.get('email')
        send_mail(
            subject=mail_subject,
            message='Verification',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[to_email],
            html_message=message,
        )
        messages.success(self.request, "Activation link is sent to your Email\nActivate Account before Login")
        return super(Registration, self).form_valid(form)


@never_cache
def activate(request, uidb64, token):
    try:
        uid = _force_start_method(urlsafe_base64_decode(uidb64))
        user = models.Student.objects.get(username=uid)
    except:
        user = None
    print(account_activation_token.check_token(user, token))
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Thank you for your email confirmation. Now you can login your account.')
        return redirect('student:login')
    else:
        return HttpResponse('Activation link is invalid!')


@never_cache
def login_view(request, *args, **kwargs):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        try:
            user = models.Student.objects.get(username=username)
        except User.DoesNotExist:
            user = None

        if user is not None:
            if user.is_active:
                user_id = authenticate(username=username, password=password)
                login(request, user_id)
                request.session.set_expiry(0)   #Session will be closed right after closure of the window
                request.session.__setitem__('image', user.profile_image.url)
                messages.success(request, 'successfully logged in')
                if request.GET.get('next'):
                    return redirect(request.GET.get('next'))
                else:
                    return redirect('student:dashboard', user.username)
            else:
                messages.error(request, 'You did not verify your email')
            return redirect('student:signup')

        try:
            user = User.objects.get(username=username)
            if not user.is_active:
                messages.error(request, 'You did not verify your email')
            else:
                messages.error(request, "Password did not match. Try again")
            return redirect('student:login')

        except User.DoesNotExist:
            messages.error(request, "User Not found please student")
            return redirect('student:signup')

    else:
        return render(request, 'student/login.html')


@never_cache
def logout_view(request):
    logout(request)
    messages.success(request, 'Logged Out')
    return redirect('student:login')


class ProfileView(generic.DetailView):
    model = models.Student
    template_name = 'student/profile.html'


class DeleteStudentProfile(UserPassesTestMixin, generic.DeleteView):
    model = models.Student

    def get_success_url(self):
        return self.request.GET.get('next')

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def test_func(self):
        return self.request.user.groups.filter(name='HOD').exists()

    def handle_no_permission(self):
        messages.error(self.request, 'No Permission')
        raise PermissionDenied


class StudentDashboard(LoginRequiredMixin, generic.DetailView):
    model = models.Student
    template_name = 'student/dashboard.html'

    def get_context_data(self, **kwargs):
        user = super().get_object()
        context = super().get_context_data(**kwargs)
        context['subjects'] = user.subjects.all()
        if Exam.objects.exists():
            exam = Exam.objects.latest()
            if exam.is_available:
                context['papers'] = exam.questionpaper_set.filter(subject__in=user.subjects.all())

        context['notification'] = models.Message.objects.filter(student=user, status=False)
        return context

    def post(self, *args, **kwargs):
        instance = self.get_object()
        try:
            subject = Subject.objects.get(code=self.request.POST.get('subject_code'))
            instance.subjects.add(subject)
        except Subject.DoesNotExist:
            pass
        return redirect('student:dashboard', instance.user_id)


class ResultView(UserPassesTestMixin, generic.ListView):
    model = models.Result
    context_object_name = 'result'
    template_name = 'student/result.html'

    def get_queryset(self):
        return models.Result.objects.filter(student_id=self.kwargs.get('username'), exam__slug=self.kwargs.get('exam'),
                                            out=True)

    def test_func(self):
        return True if self.kwargs.get('username') == self.request.user.username else False

    def handle_no_permission(self):
        raise PermissionDenied


class NotificationView(generic.ListView):
    model = models.Message
    template_name = 'student/notification.html'

    def get_queryset(self):
        return models.Message.objects.filter(student__username=self.request.user.username)
