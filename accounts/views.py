# views.py
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def signup(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        confirm_password = data.get('confirm_password')

        if not username or not email or not password or not confirm_password:
            return JsonResponse({'message': 'Please fill in all fields!'}, status=400)
        
        if password != confirm_password:
            return JsonResponse({'message': 'Passwords do not match!'}, status=400)
        
        if User.objects.filter(username=username).exists():
            return JsonResponse({'message': 'Username already exists!'}, status=400)

        if User.objects.filter(email=email).exists():
            return JsonResponse({'message': 'Email already registered!'}, status=400)

        try:
            user = User.objects.create_user(username=username, email=email, password=password)
            return JsonResponse({'message': 'Sign up successful!'}, status=201)
        except Exception as e:
            return JsonResponse({'message': str(e)}, status=400)

    return JsonResponse({'message': 'Invalid method'}, status=405)

@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return JsonResponse({'message': 'Please fill in all fields!'}, status=400)

        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)
            return JsonResponse({'message': 'Login successful!'}, status=200)
        else:
            return JsonResponse({'message': 'Invalid username or password.'}, status=401)

    return JsonResponse({'message': 'Invalid method'}, status=405)

from django.contrib.auth import logout
from django.http import JsonResponse

@csrf_exempt
def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return JsonResponse({'message': 'Logout successful!'}, status=200)
    return JsonResponse({'message': 'Invalid method'}, status=405)
