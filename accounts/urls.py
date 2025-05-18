from django.urls import path, include
from . import views
from .views import contact_view, verify_reset_otp



urlpatterns = [
    path('api/user/', views.signup, name='signup'),           # FIXED: renamed to views.signup
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('api/login/', views.login_view, name='login'),
    path('api/logout/', views.logout_view, name='logout'),     # Optional: logout
    path('contact/', views.contact_view, name='contact'),
    path('verify-reset-otp/', verify_reset_otp, name='verify-reset-otp'),
    path('api/auth/forgot-password/', views.send_reset_otp, name='forgot_password'),
]