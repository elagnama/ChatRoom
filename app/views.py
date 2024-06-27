from datetime import datetime
from django.contrib.auth.forms import AuthenticationForm
from django.core.mail import send_mail, EmailMessage
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.db import IntegrityError
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from .token import generatorToken
from djangoProject1 import settings


def index(request):
    return render(request, 'index1.html', context={"date": datetime.today()})


def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        firstname = request.POST['firstname']
        Lastname = request.POST['Lastname']
        address = request.POST['address']
        Password = request.POST['Password']
        password1 = request.POST['password1']

        if Password != password1:
            messages.error(request, 'Passwords do not match')
            return redirect('register')

        try:
            user = User.objects.create_user(username=username, password=Password, email=address)
            user.first_name = firstname
            user.last_name = Lastname
            user.is_active = False
            user.save()
            messages.success(request, 'Account created successfully')
            subject = "Bienvenue dans ton chat"
            message = "Bienvenue " + user.first_name + " " + user.last_name + " dans ton chat"
            from_email = settings.EMAIL_HOST_USER
            to_list = [user.email]
            send_mail(subject, message, from_email, to_list, fail_silently=False)
            current_site = get_current_site(request)
            email_subject = 'Activate your account'
            message_confirm = render_to_string("emailconfirm.html", context={
                "name": user.first_name,
                "domain": current_site.domain,
                "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                "token": generatorToken.make_token(user)
            })
            email = EmailMessage(
                email_subject,
                message_confirm,
                settings.EMAIL_HOST_USER,
                [user.email]
            )
            email.fail_silently = False
            email.send()
            return redirect('login')
        except IntegrityError:
            messages.error(request, 'Username already exists')
            return redirect('register')
    return render(request, 'index2.html')



def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['Password']
        try:
            user = User.objects.get(username=username)
            user = authenticate(request, username=username, password=password)
            if user is not None:
                auth_login(request, user)
                return redirect('index')
            else:
                messages.error(request, 'Invalid username or password')
                return redirect('login')
        except User.DoesNotExist:
            messages.error(request, 'User does not exist')
    return render(request, 'Login.html')


def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        my_user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        my_user = None
    if my_user is not None and generatorToken.check_token(my_user, token):
        my_user.is_active = True
        my_user.save()
        messages.add_message(request,messages.SUCCESS, "You are account is activated you can login by filling the form below.")
        return render(request,"Login.html",{'messages':messages.get_messages(request)})
    else:
        messages.add_message(request,messages.ERROR, 'Activation failed please try again')
        return render(request,'index1.html',{'messages':messages.get_messages(request)})

def logout(request):
    auth_logout(request)
    messages.success(request, f'You have been logged out')
    return redirect('index')

def chat(request):
    return render(request, 'chat.html')


