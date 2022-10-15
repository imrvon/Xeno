from decimal import Context
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from validate_email import validate_email
from .models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.urls import reverse
from helpers.decorators import auth_user_should_not_access
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str, DjangoUnicodeDecodeError
from .utils import generate_token
from django.core.mail import EmailMessage
from django.conf import settings
from django.views import View
import threading
from django.views.generic import DetailView
from blog.forms import EditProfileForm




# Create your views here.

class EmailThread(threading.Thread):

    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)
    
    def run(self):
        self.email.send()


# Send Activation Mail
def send_activation_mail(user, request):
    current_site = get_current_site(request)
    email_subject = 'Activate your Xenocoders Account'
    email_body = render_to_string('authentication/activate.html', {
        'user':user,
        'domain': current_site,
        'uid':urlsafe_base64_encode(force_bytes(user.pk)),
        'token': generate_token.make_token(user),
        'protocol': 'https' if request.is_secure() else 'http'
    })

    email=EmailMessage(subject=email_subject,
    body=email_body,
    from_email=settings.EMAIL_FROM_USER,
    to=[user.email]
    )

    EmailThread(email).start()


# Register View
@auth_user_should_not_access
def register(request):
    if request.method == "POST":
        context={'has_error': False, 'data':request.POST}
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')

        if len(password)<8:
            messages.error(request, 'Password is less than 8 characters')
            context['has_error'] = True
        
        if password != password2:
            messages.error(request, 'Password mismatch')
            context['has_error'] = True
        
        if not validate_email(email):
            messages.error(request, 'Enter a valid email address')
            context['has_error'] = True
        
        if not username:
            messages.error(request, 'Username is required')
            context['has_error'] = True
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username is taken. Choose another one')
            context['has_error'] = True
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'There is already an account associated with this email.')
            context['has_error'] = True
        
        if context['has_error']:
            return render(request, 'authentication/register.html', context)
        
        user=User.objects.create_user(username=username, email=email)
        user.set_password(password)
        user.save()

        if not context['has_error']:

            send_activation_mail(user, request)

            messages.success(request, f'Dear {user.username}, please visit your mail {user.email} inbox and click on received activation link to confirm and complete registration. Note: Check your spam folder.')

            return redirect('login')

    return render(request, 'authentication/register.html')


# Log In View
@auth_user_should_not_access
def login_user(request):
    if request.method == "POST":
        context={'has_error': False, 'data':request.POST}
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username,password=password)

        if user and not user.is_email_verified:
            messages.error(request, 'Email is not verified. Please check your mail inbox.')
            return render(request, 'authentication/login.html', context)

        if not user:
            messages.error(request, 'invalid credentials, try again')
            return render(request, 'authentication/login.html', context)
        
        login(request, user)
        messages.success(request, f'Welcome {user.username}')

        


        return redirect(reverse('user_profile', args=[user.pk]))
        

    return render(request, 'authentication/login.html')


# Log Out View
def logout_user(request):

    logout(request)
    messages.success(request, 'Successfully Logged Out')

    return redirect(reverse('login'))


# Activate User View
def activate_user(request, uidb64, token):

    try:
        uid=force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    
    except Exception as e:
        user = None
    
    if user and generate_token.check_token(user, token):
        user.is_email_verified = True
        user.save()
        
        messages.success(request, 'Email Verified and Account Successfully Activated. You Can Now Log In')
        return redirect(reverse('login'))

    return render(request, 'authentication/activation-failed.html', {'user':user})

# Home View
def home(request):
    return render(request, 'authentication/index.html')



class RequestPasswordResetEmail(View):
    def get(self, request):
        return render(request, 'authentication/reset-password.html')

    def post(self, request):

        email=request.POST['email']
        context={
            'data':request.POST
        }

        if not validate_email(email):
            messages.error(request, 'Please supply a valid email')
            return render(request, 'authentication/request-password.html', context)
        
        current_site = get_current_site(request)

        user = User.objects.filter(email=email)

        if user.exists():
            email_subject = 'Password Reset of your Xenocoders Account'
            
            email_contents = {
                'user':user[0],
                'domain': current_site.domain,
                'uid':urlsafe_base64_encode(force_bytes(user[0].pk)),
                'token': PasswordResetTokenGenerator().make_token(user[0]),
                'protocol': 'https' if request.is_secure() else 'http'
            }

            link = reverse('reset-user-password', kwargs={
                'uidb64':email_contents['uid'], 'token':email_contents['token']})
            
            reset_url = 'http://'+current_site.domain+link

            email=EmailMessage(
                email_subject,
                'Hi there, click the link below to reset your password. \n' + reset_url,
                'noreply@xenocoders.com',
                [email],
            )

            EmailThread(email).start()

        messages.success(request, 'We have sent you an email to reset your password')

        return render(request, 'authentication/reset-password.html')


class CompletePasswordReset(View):
    def get(self, request, uidb64, token):

        context = {
            'uidb64': uidb64,
            'token': token
        }

        try:
            user_id = force_str(urlsafe_base64_decode(uidb64))

            user = User.objects.get(pk=user_id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                messages.info(request, 'Password reset link is invalid. Please request a new one.')
                return render(request, 'authentication/reset-password.html')

        except Exception as identifier:

            pass
        
        return render(request, 'authentication/set-new-password.html', context)

    def post(self, request, uidb64, token):
        context = {
            'uidb64': uidb64,
            'token': token
        }

        password=request.POST['password']
        password2=request.POST['password2']

        if password != password2:
            messages.error(request, 'Passwords do not match')
            return render(request, 'authentication/set-new-password.html', context)
        
        if len(password)<8:
            messages.error(request, 'Password is less than 8 characters')
            return render(request, 'authentication/set-new-password.html', context)

        try:
            user_id = force_str(urlsafe_base64_decode(uidb64))

            user = User.objects.get(pk=user_id)
            user.set_password(password)
            user.save()

            messages.success(request, 'Password was changed successfully. Kindly log in with new password.')
            return redirect('login')

        except Exception as identifier:
            messages.info(request, 'Something went wrong. Try again.')
            return render(request, 'authentication/set-new-password.html', context)


class ShowProfilePageView(DetailView):
    model = User
    template_name = "authentication/profile.html"

    def get_context_data(self, *args, **kwargs):
        users = User.objects.all()
        context = super(ShowProfilePageView, self).get_context_data( *args, **kwargs)

        current_page_user = get_object_or_404(User, id=self.kwargs['pk'])
        posts = current_page_user.blog_posts.all()

        context = {
            "current_page_user": current_page_user,
            "posts": posts,
        }
        # context["current_page_user"] = current_page_user
        # context["posts"] = posts
        return context


def edit_profile(request, pk):
    form = EditProfileForm
    if request.method == 'POST':
        form = EditProfileForm(request.POST)
        if form.is_valid():
            form.instance.user = request.user

    context = {
        "form": form
    }
    return render(request, "authentication/edit_profile.html", context)