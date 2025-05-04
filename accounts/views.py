from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

# Supabase setup
from supabase import create_client

SUPABASE_URL = "https://lngdoqimxolarajflobo.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxuZ2RvcWlteG9sYXJhamZsb2JvIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0NDQyNDkwNCwiZXhwIjoyMDYwMDAwOTA0fQ.wX3liJEy4u2BXmD8n9yx_QjdCJO68gekl0gR2GBZf9s"  # Replace this with your actual service key (keep it secret!)
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

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
            # Create user in Django
            user = User.objects.create_user(username=username, email=email, password=password)

            # Register user in Supabase Auth
            try:
                supabase.auth.sign_up({
                    "email": email,
                    "password": password
                })
                print("User registered in Supabase Auth")
            except Exception as e:
                print("Supabase Auth signup failed:", str(e))

            # Insert into 'customers' table
            user_data = {
                "django_user_id": user.id,
                "username": user.username,
                "email": user.email,
            }

            try:
                result = supabase.table("customers").select("id").eq("django_user_id", user_data["django_user_id"]).execute()
                if not result.data:
                    supabase.table("customers").insert(user_data).execute()
                    print("User inserted into Supabase table")
                else:
                    print("User already exists in Supabase table")
            except Exception as e:
                print("Error inserting into Supabase table:", str(e))

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

            # Supabase Auth login
            try:
                supabase_auth = supabase.auth.sign_in_with_password({
                    "email": user.email,
                    "password": password
                })
                access_token = supabase_auth.get('session', {}).get('access_token')
                if not access_token:
                    return JsonResponse({'message': 'Supabase login successful, but no access token found.'}, status=200)
            except Exception as e:
                access_token = None
                print("Supabase Auth login failed:", str(e))

            # Sync to 'customers' table if needed
            user_data = {
                "django_user_id": str(user.id),
                "username": user.username,
                "email": user.email,
            }

            try:
                result = supabase.table("customers").select("id").eq("django_user_id", user_data["django_user_id"]).execute()
                if not result.data:
                    supabase.table("customers").insert(user_data).execute()
                    message = 'Login successful, user synced with Supabase!'
                else:
                    message = 'Login successful, user already synced!'
            except Exception as e:
                message = f"Login okay, but Supabase table sync failed: {str(e)}"

            return JsonResponse({
                'message': message,
                'supabase_token': access_token  # Optional: return this for frontend use
            }, status=200)

        else:
            return JsonResponse({'message': 'Invalid username or password.'}, status=401)

    return JsonResponse({'message': 'Invalid method'}, status=405)


@csrf_exempt
def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return JsonResponse({'message': 'Logout successful!'}, status=200)
    return JsonResponse({'message': 'Invalid method'}, status=405)
