from django.urls import path, include
from . import views

urlpatterns = [
    path('api/user/', views.signup, name='signup'),           # FIXED: renamed to views.signup
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('api/login/', views.login_view, name='login'),
    path('api/logout/', views.logout_view, name='logout'),     # Optional: logout
]