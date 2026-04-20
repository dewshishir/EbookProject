from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.core.exceptions import ValidationError
import stripe
from django.contrib.auth import get_user_model
from subscriptions.models import Subscription
from django.utils import timezone


User = get_user_model()

# Create your views here.
@csrf_protect
def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = auth.authenticate(email=email, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect('/')
        else:
            messages.info(request, 'Invalid credentials')
            return redirect('login')
    return render(request, 'login.html')


def logout(request):
    auth.logout(request)
    return redirect('/')

@csrf_protect
# def signup(request):
#     try:
#         if request.method == 'POST':
#             if 'first_name' in request.POST:
#                 first_name = request.POST['first_name']
#             else:
#                 first_name = ''
#             if 'last_name' in request.POST:
#                 last_name = request.POST['last_name']
#             else:
#                 last_name = ''
#             profile_pic = request.FILES.get('recipe_img')

#             email = request.POST['email']
#             password1 = request.POST['password1']
#             password2 = request.POST['password2']
#             if 'email' in request.POST:
#                 username = request.POST['email']
#             else:
#                 messages.info(request, 'Email is required')
#                 return redirect('signup')
#             if password1==password2:
#                 if User.objects.filter(email=email).exists():
#                     messages.info(request, 'Email already eixst')
#                     return redirect('signup')
#                 else:
#                     user = User.objects.create_user(first_name=first_name, last_name=last_name, username=username,email=email,password=password1, profile_pic=profile_pic)
#                     user.save();
#                     return redirect('login')

#             else:
#                 messages.info(request, 'Password do not match')
#                 return redirect('signup')
#     except Exception as e:
#         messages.info(request, e)
#         return redirect('signup')

        
    
#     return render(request, 'signup.html')

def signup(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        profile_pic = request.FILES.get('profile_pic')
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 != password2:
            messages.info(request, 'Passwords do not match')
            return redirect('signup')

        if User.objects.filter(email=email).exists():
            messages.info(request, 'Email already exists')
            return redirect('signup')

        user = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            username=email,
            profile_pic=profile_pic
        )
        user.set_password(password1)  # Use set_password to hash the password
        try:
            user.full_clean()  # Validate the model instance
        except ValidationError as e:
            messages.error(request, e.message_dict)
            return redirect('signup')
        
        user.save()
        return redirect('login')

    return render(request, 'signup.html')


def user_page(request):
    if request.user.is_authenticated:
        subscriptions = Subscription.objects.filter(user=request.user)
        status = False
        current_time = timezone.now()
        expire_time = current_time
        for sub in subscriptions:
            if sub.expires_at and sub.expires_at > current_time:
                status = True
                break
        for sub in subscriptions:
            if sub.expires_at and sub.expires_at > expire_time:
                expire_time = sub.expires_at

        return render(request, 'userpage.html', {'subscription_status': status, 'expire_time': expire_time})
    return render(request, 'userpage.html')


def membership(request):
    if request.method == 'POST':
        membership = request.POST['membership']
        amount = 1.99
        if membership == 'daily':
            amount = 1.99
        elif membership == 'monthly':
            amount = 9.99
        elif membership == 'yearly':
            amount = 89.99

        stripe.api_key = "sk_test_51PZHX8GNnECLqhp0k2VnJlnqx7Q1Q8z0TZ0lmmYeQbP4aOVJR5WNi6ocgIJP5USwLPZvYzClFM9oYTJ4BD3NyuUY00Is4FaxXv"
        
        customer = stripe.Customer.create(
            email=request.user.email,
        )

        charge = stripe.Charge.create(
            customer=customer,
            amount= amount * 1000,
            currency='usd',
            description='Membership'
        )


    return render(request, 'membership.html')


def profileEdit(request):
    if request.method=='POST':
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        profile_pic = request.FILES.get('profile_pic')
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        if first_name != None:
            User.first_name = first_name
        if last_name != None:
            User.last_name = last_name
        if profile_pic!=None:
            User.profile_pic = profile_pic
        if password1 != None and password2 != None and password1 == password2:
            User.password = password1

        # User.save()
        return redirect('userpage')
    return render(request, 'profileEdit.html')