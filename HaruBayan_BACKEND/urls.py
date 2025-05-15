# """
# URL configuration for HaruBayan_BACKEND project.

# The `urlpatterns` list routes URLs to views. For more information please see:
#     https://docs.djangoproject.com/en/5.1/topics/http/urls/
# Examples:
# Function views
#     1. Add an import:  from my_app import views
#     2. Add a URL to urlpatterns:  path('', views.home, name='home')
# Class-based views
#     1. Add an import:  from other_app.views import Home
#     2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
# Including another URLconf
#     1. Import the include() function: from django.urls import include, path
#     2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
# """
# # from django.contrib import admin
# # from django.urls import path, include

# # urlpatterns = [
# #     path('admin/', admin.site.urls),
# #     path('api/auth/', include('djoser.urls')),              # Djoser basic URLs (signup/login/logout)
# #     path('api/auth/jwt/', include('djoser.urls.jwt')),      # JWT-specific URLs (for JWT token-based auth)
# # ]

# from django.urls import path
# from django.contrib.auth.views import LoginView

# # urlpatterns = [
# #     path('api/auth/login/', LoginView.as_view(), name='login'),  # Session login endpoint
# #     path('admin/', admin.site.urls),
# #     path('api/auth/', include('djoser.urls')),
# #     path('api/auth/jwt/', include('djoser.urls.jwt')),
# # ]

# # Remove custom login and use djoser authentication
# urlpatterns = [
#     path('admin/', admin.site.urls),
#     path('api/auth/', include('djoser.urls')),
#     path('api/auth/jwt/', include('djoser.urls.jwt')),  # JWT Authentication
# ]


# # from django.urls import path
# # from djoser import views as djoser_views

# # urlpatterns = [
# #     path('api/auth/users/', djoser_views.UserCreate.as_view(), name='user-create'),
# # ]

# from django.contrib import admin  # <-- Add this import statement
# from django.urls import path, include

# urlpatterns = [
#     path('admin/', admin.site.urls),  # This should now work
#     path('api/auth/', include('djoser.urls')),  # If you're using djoser for authentication
#     path('api/auth/jwt/', include('djoser.urls.jwt')),  # For JWT auth (if needed)
#     path('api/auth/login/', views.login_view, name='login'),
# ]

from django.urls import path, include
from django.contrib import admin
from accounts import views

urlpatterns = [
    path('admin/', admin.site.urls),
    # Custom signup and login URLs
    path('api/auth/signup/', views.signup, name='signup'),
    path('api/auth/login/', views.login_view, name='login'),
    path('api/', include('accounts.urls')),
    path('', include('accounts.urls')),
]
