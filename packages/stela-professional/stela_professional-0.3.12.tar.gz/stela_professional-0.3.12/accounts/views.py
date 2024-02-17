from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import PasswordResetForm
from django.conf import settings
from django.core.mail import send_mail, EmailMultiAlternatives
from django.utils.html import strip_tags
from django.utils import timezone
from django.http.response import JsonResponse
from django.shortcuts import redirect, render
from django.contrib import messages
from stela_control.forms import LoginForm
from stela_control.forms import PwdResetForm, RegistrationForm, UserEditForm, CleanForm, UserLoginForm, PwdResetConfirmForm
from .models import UserBase
from stela_control.models import DataEmail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from .token import account_activation_token
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext_lazy as _
import re

# Create your views here.
@login_required
def profile_view(request):
    return render(request, 'link-zone/user/profile/profile.html')

def confirm_view(request):

    return render(request, 'accounts/registration/confirmation_email.html')

def account_register(request):
    date = timezone.now()
    if request.method == 'POST':
        registerForm = RegistrationForm(request.POST)
        if registerForm.is_valid():
            user = registerForm.save(commit=False)
            user.email = registerForm.cleaned_data['email']
            user.set_password(registerForm.cleaned_data['password'])
            user.is_active = False
            user.save()
            if UserBase.objects.filter(newsletter=True):
                 data = DataEmail.objects.filter(email=user.email)
                 if data.exists():
                    pass
                 else:
                    DataEmail.objects.create(
                         email = user.email,
                         date = date
                 ) 
            current_site = get_current_site(request)
            subject = _('Activate your account')
            html_content = render_to_string('emails/registration/confirmation.html', {
                        'user': user,           
                        'domain': current_site.domain,
                        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                        'token': account_activation_token.make_token(user),
                        })
            text_content = strip_tags(html_content)

            email = EmailMultiAlternatives(
                subject,
                text_content,
                settings.DEFAULT_EMAIL,
                [user.email]
            )
            email.attach_alternative(html_content, "text/html")
            email.send()

            subject = _('New User On Your Site')
            html_content = render_to_string('emails/registration/alert.html', {
                        'user': user,           
                        'domain': current_site.domain,
                        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                        'token': account_activation_token.make_token(user),
                        })
            text_content = strip_tags(html_content)

            email = EmailMultiAlternatives(
                subject,
                text_content,
                settings.STELA_EMAIL,
                [settings.DEFAULT_EMAIL]
            )
            email.attach_alternative(html_content, "text/html")
            email.send()
            
            return redirect('accounts:confirm')

    else:
        registerForm = RegistrationForm()
    return render(request, 'accounts/registration/register.html',{'form':registerForm})

def request(request):
    action = request.POST.get('action')
    print(action)
    
    if action == "checkEmail":
        pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        email = request.POST.get("user_input")
        if UserBase.objects.filter(email=email).exists():
            response = JsonResponse({'error': _('email not available')})
        elif not pattern.match(email):
            response = JsonResponse({'error': _('Invalid email')})
        else:
            response = JsonResponse({'success': _('email available')})
        return response

    if action == "checkUsername":
        username = request.POST.get("user_input")
        if UserBase.objects.filter(username=username).exists():
            response = JsonResponse({'error': _('username not available')})
            
        elif not re.match(r'^[a-z0-9_]+$', username):
            response = JsonResponse({'error': _('invalid username only lower case, numbers and (_) accepted')})
        
        else:
            response = JsonResponse({'success': _('username available')})
        
        return response
        
    if action == "checkPassword":
        password = request.POST.get("password")
        
        if len(password) < 8:
            response = JsonResponse({'error': _('Password must be at least 8 characters long')})
        
        elif not re.match(r'^[a-zA-Z0-9*.$_]+$', password):
            response = JsonResponse({'error': _('Password must contain only alphanumeric and special characters (a-zA-Z0-9*$_.)')})
        
        elif password.isalpha():
            response = JsonResponse({'error': _('Password must contain at least one number')})
            
        else:
            response = JsonResponse({'success': _('Password is valid')})

        return response

    if action == "matchPassword":
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        if password1 != password2:
            response = JsonResponse({'error': _('Password dismatch.')})
        else:
            response = JsonResponse({'success': _('Password match')})
        return response
    
def clean_address(request):
    user = request.user
    data = UserBase.objects.get(pk=user.id)
    profile = CleanForm(instance=data)

    event = "Clean Address"

    context={
        'event': event,
        'profile': profile
    }

    return render(request, 'accounts/user/clean_user.html',context)

def addressFormStela(request):
    user = request.user
    data = UserBase.objects.get(pk=user.id)
    profile = CleanForm(instance=data)
    form = CleanForm(request.POST, request.FILES, instance=data)
        
    if form.is_valid():
            form = profile.save(commit=False)
            form.user = user
            form.save()
            form.save(using='master')

            return redirect("http://stela.localhost:8000/cart")

def password_reset(request):
    if request.method == 'POST':
        registerForm = PwdResetForm(request.POST)
        if registerForm.is_valid():
            data = registerForm.cleaned_data['email']
            user_email = UserBase.objects.filter(email=data)
            if user_email.exists():
                for user in user_email:

                    current_site = get_current_site(request)
                    subject = _('Password Reset')
                    html_content = render_to_string('emails/registration/password_reset_email.html', {
                                'user': user,       
                                'email': user.email,    
                                'domain': current_site.domain,
                                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                                'token': account_activation_token.make_token(user),
                                })
                    text_content = strip_tags(html_content)

                    email = EmailMultiAlternatives(
                        subject,
                        text_content,
                        settings.DEFAULT_EMAIL,
                        [user.email]
                    )
                    email.attach_alternative(html_content, "text/html")
                    email.send()

                    messages.success(request, _('We have sent recovery link.'))
                    return redirect('accounts:password_reset_done')
    else:
        registerForm = PwdResetForm()
        
    return render(request, 'accounts/user/password_reset_form.html',{'form':registerForm})

def new_password_activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = UserBase.objects.get(pk=uid)
    except Exception as e:
        user = None
        print(e)

    if user is not None and account_activation_token.check_token(user, token):
        if request.method == 'POST':
            form = PwdResetConfirmForm(user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, _("Your new password has been set."))
                return redirect('/accounts/login/')
            else:
                for error in list(form.errors.values()):
                    messages.error(request, error)

        form = PwdResetConfirmForm(user)
        return render(request, 'accounts/user/password_reset_done.html', {
            'form': form,
            'call': 'password reset granted'
            })
    else:
        messages.error(request, _("Link is expired"))

    messages.error(request, _('Something went wrong, redirecting back to account login'))
    return redirect('/accounts/login/')

def account_activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = UserBase.objects.get(pk=uid)
    except:
        pass
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        messages.success(request, 'Your account has been activated.')
        return redirect('linkzone:console')
    else:
        return render(request, 'accounts/registration/activation_invalid.html') 

@login_required
def edit_details(request):

    if request.method == 'POST':
        user_form = UserEditForm(instance=request.user, data=request.POST)

        if user_form.is_valid():
            user_form.save()
    else:
        user_form = UserEditForm(instance=request.user)
    return render(request, 'link-zone/user/profile/edit_details.html', {'user_form': user_form}) 

@login_required
def delete_user(request):
    user = UserBase.objects.get(username=request.user)
    user.is_active = False
    user.save()
    logout(request)
    return redirect('accounts:delete_confirm')

def logout_view(request):
    logout(request)
    return redirect('/accounts/login/')
