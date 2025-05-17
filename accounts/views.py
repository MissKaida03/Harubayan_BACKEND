import json
import random
from django.core.cache import cache
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.crypto import get_random_string
from django.utils import timezone
from datetime import timedelta
from .models import EmailOTP
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.contrib import messages
import random
from django.contrib.auth.models import User
from django.core.mail import send_mail
from rest_framework.response import Response
from rest_framework.decorators import api_view

from django.core.cache import cache  # make sure this is imported

@api_view(['POST'])
def send_reset_otp(request):
    email = request.data.get('email')
    if not email:
        return Response({'detail': 'Email is required'}, status=400)

    users = User.objects.filter(email=email, is_active=True)  # ✅ Only allow verified users

    if not users.exists():
        return Response({'detail': 'User not found or not verified.'}, status=404)

    if users.count() > 1:
        return Response({'detail': 'Multiple verified users found with this email. Please contact support.'}, status=400)

    user = users.first()
    otp = str(random.randint(100000, 999999))

    cache.set(f'reset_otp_{email}', otp, timeout=600)

    send_mail(
        'Your OTP Code',
        f'Your OTP is: {otp}',
        'noreply@harubayan.com',
        [email]
    )
    return Response({'detail': 'OTP sent to email'})


from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.core.cache import cache
from django.contrib.auth import get_user_model

User = get_user_model()

@api_view(['POST'])
def verify_reset_otp(request):
    email = request.data.get('email')
    otp = request.data.get('otp')
    new_password = request.data.get('new_password')

    # Step 1: Validate required fields
    if not all([email, otp, new_password]):
        return Response({'detail': 'Missing fields. Email, OTP, and new password are required.'}, status=400)

    # Step 2: Validate OTP
    saved_otp = cache.get(f'reset_otp_{email}')
    if not saved_otp:
        return Response({'detail': 'OTP expired or not found. Please request a new one.'}, status=400)

    if saved_otp != otp:
        return Response({'detail': 'Invalid OTP. Please check and try again.'}, status=400)

    # Step 3: Find user
    users = User.objects.filter(email=email)
    if not users.exists():
        return Response({'detail': 'User not found with this email.'}, status=404)
    if users.count() > 1:
        return Response({'detail': 'Multiple users found with this email. Please contact support.'}, status=400)

    user = users.first()

    # ✅ Step 3.5: Check if account is verified
    if not user.is_active:
        return Response({'detail': 'This account is not verified yet. Cannot reset password.'}, status=403)

    # Step 4: Set the new password
    user.set_password(new_password)
    user.save()

    # Step 5: Clean up the cache
    cache.delete(f'reset_otp_{email}')

    return Response({'detail': 'Password reset successful. You may now log in.'}, status=200)



@csrf_exempt
def contact_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            name = data.get('name')
            email = data.get('email')
            message = data.get('message')

            subject = f'New Contact Form Submission from {name}'
            body = f'Name: {name}\nEmail: {email}\n\nMessage:\n{message}'

            send_mail(
                subject,
                body,
                email,
                ['harubayan.official@gmail.com'],
            )

            return JsonResponse({'message': 'Your message has been sent!'}, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid method'}, status=405)


# --- Supabase Setup ---
from supabase import create_client

SUPABASE_URL = "https://lngdoqimxolarajflobo.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxuZ2RvcWlteG9sYXJhamZsb2JvIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0NDQyNDkwNCwiZXhwIjoyMDYwMDAwOTA0fQ.wX3liJEy4u2BXmD8n9yx_QjdCJO68gekl0gR2GBZf9s"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


@csrf_exempt
def signup(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)  # 🟢 MODIFIED: Safer JSON parsing
        except json.JSONDecodeError:
            return JsonResponse({'message': 'Invalid JSON'}, status=400)

        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        re_password = data.get('re_password')

        if not username or not email or not password or not re_password:
            return JsonResponse({'message': 'Please fill in all fields!'}, status=400)

        if password != re_password:
            return JsonResponse({'message': 'Passwords do not match!'}, status=400)

        if User.objects.filter(username=username).exists():
            return JsonResponse({'message': 'Username already exists!'}, status=400)

        if User.objects.filter(email=email).exists():
            return JsonResponse({'message': 'Email already registered!'}, status=400)

        try:
            user = User.objects.create_user(username=username, email=email, password=password)
            user.is_active = False
            user.save()

            try:
                supabase.auth.sign_up({"email": email, "password": password})
                print("User registered in Supabase Auth")
            except Exception as e:
                print("Supabase Auth signup failed:", str(e))

            user_data = {
                "django_user_id": user.id,
                "username": user.username,
                "email": user.email,
            }
            try:
                result = supabase.table("customers").select("id").eq("django_user_id", user.id).execute()
                if not result.data:
                    supabase.table("customers").insert(user_data).execute()
                    print("User inserted into Supabase table")
                else:
                    print("User already exists in Supabase table")
            except Exception as e:
                print("Error inserting into Supabase table:", str(e))

            otp = get_random_string(length=6, allowed_chars='0123456789')
            EmailOTP.objects.update_or_create(user=user, defaults={'otp': otp, 'created_at': timezone.now()})

            send_mail(
                'Your HaruBayan OTP Code',
                f'Hello {username},\n\nYour OTP is: {otp}\nIt expires in 10 minutes.',
                'harubayan.official@gmail.com',
                [email],
                fail_silently=False,
            )

            return JsonResponse({'message': 'User created. OTP sent to email.'}, status=201)  # 🟢 MODIFIED: 201 status

        except Exception as e:
            return JsonResponse({'message': f'Error creating user: {str(e)}'}, status=500)  # 🟢 MODIFIED: safer error

    return JsonResponse({'message': 'Invalid method'}, status=405)


@csrf_exempt
def verify_otp(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)  # 🟢 MODIFIED
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        username = data.get('username')
        otp_input = data.get('otp')

        try:
            user = User.objects.get(username=username)
            otp_entry = EmailOTP.objects.get(user=user)

            if otp_entry.otp == otp_input and not otp_entry.is_expired():
                user.is_active = True
                user.save()
                otp_entry.delete()
                return JsonResponse({'message': 'Account verified successfully.'})
            else:
                if otp_entry.is_expired():
                    return JsonResponse({'error': 'OTP has expired.'}, status=400)
                return JsonResponse({'error': 'Invalid OTP.'}, status=400)

        except (User.DoesNotExist, EmailOTP.DoesNotExist):
            return JsonResponse({'error': 'User or OTP not found.'}, status=404)

    return JsonResponse({'message': 'Invalid method'}, status=405)


@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)  # 🟢 MODIFIED
        except json.JSONDecodeError:
            return JsonResponse({'message': 'Invalid JSON'}, status=400)

        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return JsonResponse({'message': 'Please fill in all fields!'}, status=400)

        user = authenticate(request, username=username, password=password)

        if user is not None:
            if not user.is_active:
                return JsonResponse({'message': 'Please verify your email before logging in.'}, status=403)

            auth_login(request, user)

            try:
                supabase_auth = supabase.auth.sign_in_with_password({"email": user.email, "password": password})
                access_token = supabase_auth.get('session', {}).get('access_token')  # 🟢 FIXED: safer token access
            except Exception as e:
                access_token = None
                print("Supabase Auth login failed:", str(e))

            return JsonResponse({
                'message': 'Login successful!',
                'supabase_token': access_token
            }, status=200)

        return JsonResponse({'message': 'Invalid username or password.'}, status=401)

    return JsonResponse({'message': 'Invalid method'}, status=405)


@csrf_exempt
def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return JsonResponse({'message': 'Logout successful!'}, status=200)
    return JsonResponse({'message': 'Invalid method'}, status=405)
