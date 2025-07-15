from django.shortcuts import render,redirect,get_object_or_404
from .models import Number
from book.models import Book
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
import pyotp
from django.conf import settings
from django.core.mail import send_mail
from django.http import JsonResponse
from django.contrib.auth import update_session_auth_hash
from datetime import datetime

# Create your views here.



#redirect
def amenities(request):
    return render(request, 'login/amenities.html')

def contact(request):
    return render(request, 'login/contact.html')

def about_us(request):
    return render(request, 'login/about.html')


def index(request):
    current_month = datetime.now().month
    current_year = datetime.now().year
    
    # Get booking count for current month
    monthly_bookings = Book.objects.filter(
        start_date__month=current_month,
        start_date__year=current_year
    ).count()
    
    return render(request, 'login/homepage.html', {
        'monthly_bookings': monthly_bookings,
        'current_month': current_month,
        'current_year': current_year,
    })
    

def login_view(request):
    if request.method == "POST":
        # Check if user is already authenticated (should be *before* processing POST data)
        if request.user.is_authenticated:
            return render(request, 'login/login.html', {
                'error_message': 'Please log out of your current account before signing in with another one.'
            })

        # Get credentials from POST data
        username = request.POST.get("username")
        password = request.POST.get("password")

        # Validate credentials
        if not username or not password:
            return render(request, 'login/login.html', {
                'error_message': 'Please provide both username and password.'
            })

        # Authenticate user
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)  # Critical: Actually log the user in
            request.session['username'] = username  # Optional: Store in session
            return redirect(generate_otp)  # Ensure 'generate_otp' is a valid URL name
        else:
            return render(request, 'login/login.html', {
                'error_message': 'Invalid username or password.'
            })

    # GET request or other methods
    return render(request, 'login/login.html')


def logout_view(request):
    logout(request)
    return redirect(login_view)

def register(request):
    if request.method=="POST":
        username=request.POST.get("username")
        first_name=request.POST.get("first_name")
        last_name=request.POST.get("last_name")
        email=request.POST.get("gmail")
        number=request.POST.get("number")
        password=request.POST.get("password")

        if User.objects.filter(username=username).exists():
            messages.error(request,"username Already Exist")
        elif User.objects.filter(email=email).exists():
            messages.error(request,"Email Already Exist")
        else:
            user= User.objects.create_user(username=username, first_name=first_name, last_name=last_name, email=email, password=password)
            user.save()

            number=Number(user=user,number=number)
            number.save()

            messages.success(request,"You are now Registered")
            return redirect(login_view)

        return redirect(login_view)
    return render(request, 'login/register.html')

def generate_otp(request):
    username = request.session.get('username')
    if not username:
        return redirect('login')

    user = get_object_or_404(User, username=username)

    
    if 'otp_secret_key' not in request.session:
        request.session['otp_secret_key'] = pyotp.random_base32()

    otp_secret_key = request.session['otp_secret_key']
    totp = pyotp.TOTP(otp_secret_key)
    otp_code = totp.now()

    if request.method == 'POST':
        user_otp = request.POST.get('otp')

        # Verify if the user OTP is valid
        if totp.verify(user_otp, valid_window=1):  
            login(request, user)
            request.session.modified = True
            del request.session['otp_secret_key']
            del request.session['username']
            return redirect('index')  
        else:
            return render(request, 'login/otp.html', {
                'otp': otp_code
            })

    send_mail(
        'OTP Code',
        f'Your OTP code is: {otp_code} ',
        settings.EMAIL_HOST_USER,
        [user.email],
        fail_silently=False
    )

    return render(request, 'login/otp.html', {'otp': otp_code,})


def event_data(request):
    data=[]
    books=Book.objects.all()
    
    for book in books:
        data.append({
            "title":'Booked',
            "start":book.start_date.isoformat()
        })

    return JsonResponse(data, safe=False)


def change_profile(request):
    user=request.user
    if request.method=='POST':
        first_name = request.POST.get('first_name', user.first_name)
        last_name = request.POST.get('last_name', user.last_name)
        username = request.POST.get('username', user.username)
        email = request.POST.get('email', user.email)

        user.first_name=first_name
        user.last_name=last_name
        user.username=username
        user.email=email
        user.save()

        if user.is_superuser:
            return redirect('admin_setting')
        else:
            return redirect('user_setting')
        

def change_password(request):
    user = request.user
    error = 'Invalid current password'
    success='your password is successfully changed'
    new_password_error = 'New password and confirmation do not match'

    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if new_password == confirm_password:
            if user.check_password(current_password):  
                user.set_password(new_password) 
                user.save()
                update_session_auth_hash(request, user) 

                if user.is_superuser:
                    return render(request, 'login/admin_setting.html', {
                    'error_messages': success
                })
                else:
                    return render(request, 'login/user_setting.html', {
                    'error_messages': success
                })

                
            else:
                if user.is_superuser:
                    return render(request, 'login/admin_setting.html', {
                    'error_messages': error})
                else:
                    return render(request, 'login/user_setting.html', {
                    'error_messages': error})
                     
        else:
            if user.is_superuser:
                return render(request, 'login/admin_setting.html', {
                'error_messages': new_password_error})
            else:
                return render(request, 'login/user_setting.html', {
                'error_messages': new_password_error})


    if user.is_superuser:
        return render(request, 'login/admin_setting.html', {
        'error_messages': new_password_error})
    else:
        return render(request, 'login/user_setting.html', {
        'error_messages': new_password_error})

def user(request):
    users=User.objects.all()

    return render(request, 'login/user.html',{
        'users':users
    })        

def delete_user(request, id):
    user_to_delete = get_object_or_404(User, id=id)
    user_to_delete.delete()

    return redirect("user")


def create_admin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm = request.POST.get('confirm_password')

        if password != confirm:
            return render(request, 'create_admin.html', {
                'error': 'Passwords do not match.'
            })
        user = User.objects.create_user(username=username, email=email, password=password)
        user.is_staff = True
        user.is_superuser = True
        user.save()
        return redirect('user')
    
def user_setting(request):
    return render(request, 'login/user_setting.html')