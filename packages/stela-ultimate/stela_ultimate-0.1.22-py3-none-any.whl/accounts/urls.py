from django.contrib.auth import views as auth_views
from django.urls import path
from django.conf import settings
from django.views.generic import TemplateView
from stela_control.forms import (UserLoginForm, PwdResetForm, PwdResetConfirmForm)
from . import views
    
app_name="accounts"

urlpatterns = [
    #login
    path('login/', auth_views.LoginView.as_view(template_name='accounts/user/login.html', form_class=UserLoginForm), name="login"),
    path('logout/', views.logout_view, name="logout"),
    #register
    path('register/', views.account_register, name="register"),
    path('request/', views.request, name="request"),
    path('clean-address', views.clean_address, name="clean_address"),
    path('stela/clean-address/form/', views.addressFormStela, name="clean_address_form"),
    path('activate/<uidb64>/<token>/', views.account_activate, name="activate"),
    path('register/confirmation/', views.confirm_view, name="confirm"),
    #password reset
    path('password_reset/', views.password_reset, name='password-reset'),
    path('password_reset/password_reset_email_confirm/', TemplateView.as_view(template_name="accounts/user/password_reset_done.html"), name='password_reset_done'),
    path('password_reset_confirm/<uidb64>/<token>/', views.new_password_activate, name="password_reset_confirm"),
    path('password_reset_complete/', TemplateView.as_view(template_name="accounts/user/password_reset_done.html"), name='password_reset_complete'),
    #user profile
    path('profile/', views.profile_view, name="profile"), 
    path('profile/edit/', views.edit_details, name="edit_account"),
    path('profile/delete/', views.delete_user, name="delete_user"),
    path('profile/delete_confirm', TemplateView.as_view(template_name="accounts/delete_user.html"), name="delete_confirm"), 
]