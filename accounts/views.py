from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

# Supabase setup
from supabase import create_client

SUPABASE_URL = "https://lngdoqimxolarajflobo.supabase.co"  # Replace with your Supabase project URL
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxuZ2RvcWlteG9sYXJhamZsb2JvIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0NDQyNDkwNCwiZXhwIjoyMDYwMDAwOTA0fQ.wX3liJEy4u2BXmD8n9yx_QjdCJO68gekl0gR2GBZf9s"  # Replace with your Supabase service key (not anon key!)
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
            user = User.objects.create_user(username=username, email=email, password=password)

            # Sync with Supabase (Insert data into customers table)
            user_data = {
                "django_user_id": user.id,  # Store the Django user ID
                "username": user.username,
                "email": user.email,
            }

            try:
                # Attempt to insert into the 'customers' table
                print("Attempting to sync user with Supabase...")
                result = supabase.table("customers").select("id").eq("django_user_id", user_data["django_user_id"]).execute()
                if not result.data:
                    insert_response = supabase.table("customers").insert(user_data).execute()
                    print("Insert response:", insert_response)
                else:
                    print("User already synced with Supabase")

            except Exception as e:
                print("Error syncing with Supabase:", str(e))

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

            # Supabase duplication logic
            user_data = {
                "django_user_id": str(user.id),  # Store the Django user ID
                "username": user.username,
                "email": user.email,
            }

            try:
                print("Attempting to sync user with Supabase...")
                print("User data to insert:", user_data)

                result = supabase.table("customers").select("id").eq("django_user_id", user_data["django_user_id"]).execute()
                print("Supabase query result:", result)

                if not result.data:
                    insert_response = supabase.table("customers").insert(user_data).execute()
                    print("Insert response:", insert_response)
                    return JsonResponse({'message': 'Login successful and user synced with Supabase!'}, status=200)
                else:
                    return JsonResponse({'message': 'Login successful, user already synced with Supabase!'}, status=200)

            except Exception as e:
                return JsonResponse({'message': f"Login successful, but error syncing with Supabase: {str(e)}"}, status=200)

        else:
            return JsonResponse({'message': 'Invalid username or password.'}, status=401)

    return JsonResponse({'message': 'Invalid method'}, status=405)


@csrf_exempt
def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return JsonResponse({'message': 'Logout successful!'}, status=200)
    return JsonResponse({'message': 'Invalid method'}, status=405)
