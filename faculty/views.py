from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User, Group
from django.contrib.sites.shortcuts import get_current_site
from django.core import mail
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.urls import reverse
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from module.models import Exam, Subject
from student.models import Student, Message, Response, Result
from . import forms, models
from django.views import generic
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.core.mail import mail_admins, send_mail
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator


@method_decorator(never_cache, 'dispatch')
class Registration(generic.CreateView):
    form_class = forms.FacultySignupForm
    context_object_name = 'form'
    template_name = 'faculty/signup.html'

    def get_success_url(self):
        return reverse('faculty:login')

    def form_valid(self, form):
        form.instance.is_active = False
        domain = get_current_site(self.request).domain
        msg = render_to_string('faculty/activation.html', {'profile': form.instance, 'domain': domain})
        verifier = 'Admin'
        if form.instance.designation != 'HOD':
            try:
                hod = models.Faculty.objects.get(designation='HOD', dept=form.instance.dept)
            except:
                hod = None
            if hod:
                verifier = 'HOD'
                send_mail(subject='Faculty Signup', message='A faculty needs approval', fail_silently=True,
                          recipient_list=[hod.email],
                          connection=mail.get_connection(), html_message=msg, from_email=settings.EMAIL_HOST_USER)
                messages.success(self.request, 'Account will be verified by your HOD, you will get a confirmation mail soon')
        else:
            if models.Faculty.objects.filter(groups__name='HOD', dept=form.instance.dept).exists():
                print(55)
                messages.error(self.request,
                               'A HOD is already registered in your department, kindly contact Examination Controller')
                return redirect('faculty:signup')
            else:
                mail_admins(subject='HOD Signup', message='A HOD needs approval', fail_silently=True,
                            connection=mail.get_connection(), html_message=msg)

            messages.success(self.request,
                             """Your account will be verified by %s.
                             Kindly Login after Verification.
                             You will get a confirmation Email""" % verifier)
        return super(Registration, self).form_valid(form)


@login_required(login_url='/login/')
def activate(request, *args, **kwargs):
    if request.user.groups.filter(name='HOD').exists() or request.user.is_superuser:
        user = get_object_or_404(models.Faculty, user_id=int(kwargs.get('pk')))
        user.is_active = True
        user.is_staff = True
        user.groups.add(Group.objects.get_or_create(name=user.designation)[0])
        user.save()
        user.email_user(subject='Account Approval',
                        message='Your account is approved , you can login now',
                        from_email=settings.EMAIL_HOST_USER)
        return HttpResponse('Done')
    else:
        messages.error(request, 'Superuser access Required')
        raise PermissionDenied


@never_cache
def login_view(request, *args, **kwargs):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        try:
            user = models.Faculty.objects.get(username=username)
        except User.DoesNotExist:
            print('User model Not Exist')
            user = None

        if user is not None:
            if user.check_password(raw_password=password):
                if user.is_active:
                    user_id = authenticate(username=username, password=password)
                    login(request, user_id)
                    request.session.__setitem__('username', username)
                    request.session.__setitem__('role', user.designation)
                    request.session.__setitem__('image', user.profile_image.url)
                    messages.success(request, 'successfully logged in')
                    if request.GET.get('next'):
                        return redirect(request.GET.get('next'))
                    else:
                        return redirect('faculty:dashboard', user.user_id)
                else:
                    messages.error(request, 'Please wait for HOD to verify your Account')
                return redirect('faculty:signup')
            else:
                messages.error(request, "Password did not match. Try again")
                return redirect('faculty:login')

        else:
            try:
                user = Student.objects.get(username=username)
                messages.error(request, 'Redirected to  Student Page')
                return redirect('student:login')

            except User.DoesNotExist:
                messages.error(request, "User Does Not Found\nPlease Signup")
                return redirect('faculty:signup')

    else:
        if request.user.is_staff and request.user.username != 'admin':
            return redirect('faculty:dashboard', int(request.user.username))
        else:
            return render(request, 'faculty/login.html')


@never_cache
def logout_view(request):
    logout(request)
    messages.success(request, 'Logged Out')
    return redirect('faculty:login')


class ProfileView(UserPassesTestMixin, generic.DetailView):
    model = models.Faculty
    template_name = 'faculty/profile-detail.html'
    context_object_name = 'profile'

    def test_func(self):
        return True if self.request.user.is_staff else False

    def handle_no_permission(self):
        messages.error(self.request, 'Access Denied Login with Faculty Account')
        return redirect('faculty:login')


class DeleteFacultyProfile(UserPassesTestMixin, generic.DeleteView):
    model = models.Faculty

    def get_success_url(self):
        return self.request.GET.get('next')

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def test_func(self):
        return self.request.user.groups.filter(name='HOD').exists()

    def handle_no_permission(self):
        messages.error(self.request, 'No Permission')
        raise PermissionDenied


class FacultyDashboard(LoginRequiredMixin, generic.DetailView):
    model = models.Faculty
    template_name = 'faculty/dashboard.html'
    context_object_name = 'user'

    def get_login_url(self):
        return reverse('faculty:login')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.username != str(self.kwargs.get('pk')):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = models.Faculty.objects.get(username=self.request.user)
        context['exam'] = Exam.objects.filter(start_date__year=timezone.now().year)
        if user.dept == 'AS' and user.designation != 'HOD':
            context['subjects'] = Subject.objects.filter(sem__in=[1, 2])
            self.template_name = 'faculty/applied-science-dashboard.html'
        else:
            context['subjects'] = Subject.objects.filter(dept=user.dept)

        if user.designation == 'HOD':
            context['faculties'] = models.Faculty.objects.filter(dept=user.dept)
            if user.dept == 'AS':
                context['subjects'] = Subject.objects.filter(sem__in=[1, 2])
                context['students'] = Student.objects.filter(sem__in=[1, 2])
                self.template_name = 'faculty/applied-science-HOD.html'
            else:
                context['students'] = Student.objects.filter(dept=user.dept)
                self.template_name = 'faculty/HOD.html'

        return context


class ResponseList(UserPassesTestMixin, generic.ListView):
    template_name = 'faculty/ResponseTable.html'
    context_object_name = 'responses'

    def get_queryset(self):
        return Result.objects.filter(question_paper_id=self.kwargs.get('pk'))

    def test_func(self):
        return True if self.request.user.is_staff else False

    def handle_no_permission(self):
        messages.error(self.request, 'Access Denied Login with Faculty Account')
        return redirect('faculty:login')


class ResponseDetail(UserPassesTestMixin, generic.DetailView):
    model = Result
    template_name = 'faculty/responseDetail.html'
    context_object_name = 'response'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['q_responses'] = Response.objects.filter(question_paper_id=self.kwargs.get('paper_id'),
                                                         user__username=self.kwargs.get('username'))
        return context

    def test_func(self):
        return True if self.request.user.is_staff else False

    def handle_no_permission(self):
        messages.error(self.request, 'Access Denied Login with Faculty Account')
        return redirect('faculty:login')


def ajax_query(request, *args, **kwargs):
    dept = request.GET.get('dept')
    queryset = models.Faculty.objects.filter(dept=dept)
    json = {'data': list(queryset.values_list('first_name', 'last_name', 'user_id', 'email', 'is_active', 'dept'))}
    return JsonResponse(json)
