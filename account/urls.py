from django.urls import path
from . import views
from django.contrib.auth import views as auth_view

urlpatterns = [
    path('', views.home, name='home_page'),
    path('register', views.register, name='register_page'),
    path('login', views.my_login, name='login_page'),
    path('logout', views.user_logout, name='logout_view'),

    # password reset management :
    path(
        'reset_password',
        views.CustomPasswordResetView.as_view(template_name='password_reset.html'),
        name='reset_password'
    ),

    path(
        'reset_password/sent',
        auth_view.PasswordResetDoneView.as_view(template_name='password_reset_sent.html'),
        name='password_reset_done'
    ),

    path(
        'reset_password/<uidb64>/<token>/',
        views.CustomPasswordResetConfirmView.as_view(template_name='password_reset_form.html'),
        name='password_reset_confirm'
    ),

    path(
        'reset_password/complete',
        auth_view.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'),
        name='password_reset_complete'
    ),

    # email verification :
    path('email-verification/<uidb64>/<token>', views.email_verification, name='email_verification'),
    path('email-verification-sent', views.email_verification_sent, name='email_verification_sent'),
    path('email-verification-success', views.email_verification_success, name='email_verification_success'),
    path('email-verification-failed', views.email_verification_failed, name='email_verification_failed'),
]
