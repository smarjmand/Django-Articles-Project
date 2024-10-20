from django.shortcuts import render, redirect
from .forms import RegisterForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from .models import CustomUser as User
from django.contrib.auth.views import PasswordResetConfirmView, PasswordResetView
from django.contrib.auth.forms import SetPasswordForm, PasswordResetForm, _unicode_ci_compare
from django.contrib.sites.shortcuts import get_current_site
from .utils import user_tokenizer_generate, send_verification_email
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model


# ------------------------------------------------------------
# index page :
def home(request):
    return render(request, 'index.html')


# ------------------------------------------------------------
# to create a user ( writer/client ) and sending verification-email :
def register(request):
    form = RegisterForm()
    context = {'RegisterForm': form}

    if request.method == 'POST':
        form = RegisterForm(request.POST)

        if form.is_valid():
            user_object = form.save()
            user_object.is_active = False
            user_object.save()

            site_domain = get_current_site(request)

            send_verification_email(user=user_object, domain=site_domain)

            return redirect('email_verification_sent')

        context = {'RegisterForm': form}

    return render(request, 'register.html', context)


# ------------------------------------------------------------
# a custom form to get email/password from user ( change it to farsi ) :
class CustomAuthenticationForm(AuthenticationForm):
    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request=None, *args, **kwargs)
        self.fields['username'].label = 'ایمیل'
        self.fields['password'].label = 'گذرواژه'

        self.error_messages['inactive'] = 'ابتدا حساب کاربری خود را فعال کنید'
        self.error_messages['invalid_login'] = 'ایمیل یا گذرواژه صحیح نمی باشد'

    # for some reason, inactive-error-message didn't display, to fix it :
    def clean(self):
        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")
        user_model: User = get_user_model()

        # ----------------------------------
        # ( added this part to function )
        try:
            user = user_model.objects.get(**{user_model.USERNAME_FIELD: username})
            print('user exists: ', user.email)
            if not user.is_active:
                raise ValidationError(
                    self.error_messages["inactive"],
                    code="inactive",
                )
        except user_model.DoesNotExist:
            print('user does not exist!!')
            raise self.get_invalid_login_error()
        # ----------------------------------

        if username is not None and password:
            self.user_cache = authenticate(
                self.request, username=username, password=password
            )
            if self.user_cache is None:
                raise self.get_invalid_login_error()
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data


# ------------------------------------------------------------
# To login user :
def my_login(request):
    form = CustomAuthenticationForm()
    context = {'LoginForm': form}

    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)

        # to check if username and password are correct :
        if form.is_valid():
            username = request.POST.get('username')  # username = email
            password = request.POST.get('password')
            user = authenticate(request, username=username, password=password)

            # if user is a writer :
            if user is not None and user.is_writer is True:
                login(request, user)
                return redirect('writer_dashboard_page')

            # if user is a client :
            elif user is not None and user.is_writer is False:
                login(request, user)
                return redirect('client_dashboard_page')

        context = {'LoginForm': form}

    return render(request, 'login.html', context)


# ------------------------------------------------------------
# To logout user from account :
def user_logout(request):
    logout(request)
    return redirect('login_page')


# ------------------------------------------------------------
# To use << reset-password >> as a way to activate account :
# ( if somehow user didn't get verification-email )
class CustomPasswordResetForm(PasswordResetForm):
    def get_users(self, email):
        UserModel = get_user_model()
        email_field_name = UserModel.get_email_field_name()

        # ----------------------------------
        # only active users could get reset-password-email, so << is_active=True >> is removed :
        active_users = UserModel._default_manager.filter(
            **{
                "%s__iexact" % email_field_name: email
            }
        )
        # ----------------------------------

        return (
            u
            for u in active_users
            if u.has_usable_password()
               and _unicode_ci_compare(email, getattr(u, email_field_name))
        )


# To use custom-email-template for resetting the password :
class CustomPasswordResetView(PasswordResetView):
    form_class = CustomPasswordResetForm
    subject_template_name = 'password_reset_subject.txt'
    email_template_name = 'password_reset_email.html'


# ------------------------------------------------------------
# To modify labels ( change it to farsi ) :
class CustomSetPasswordForm(SetPasswordForm):

    def __init__(self, user, *args, **kwargs):
        super().__init__(user, *args, **kwargs)

        self.fields['new_password1'].label = 'کلمه عبور جدید'
        self.fields['new_password2'].label = 'تکرار کلمه عبور جدید'

        self.fields['new_password1'].help_text = None
        self.fields['new_password2'].help_text = None


# To use << reset-password >> as a way to activate account :
# ( if somehow user didn't get it )
class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    form_class = CustomSetPasswordForm

    def form_valid(self, form):
        user = form.save()

        # ----------------------------------
        # added to activate user's account by << reset-password-email >> :
        if not user.is_active:
            user.is_active = True
            user.save()
        # ----------------------------------

        if self.post_reset_login:
            login(self.request, user, self.post_reset_login_backend)
        return super().form_valid(form)


# ------------------------------------------------------------
# To verify user's account with verification-email :
def email_verification(request, uidb64, token):
    user_id = force_str(urlsafe_base64_decode(uidb64))
    user = User.objects.get(id=user_id)

    if user and user_tokenizer_generate.check_token(user, token):
        user.is_active = True
        user.save()
        return redirect('email_verification_success')

    return redirect('email_verification_failed')


# ------------------------------------------------------------
# To show messages to user through verifying his/her account :
def email_verification_sent(request):
    return render(request, 'email_verification_sent.html')


def email_verification_success(request):
    return render(request, 'email_verification_success.html')


def email_verification_failed(request):
    return render(request, 'email_verification_failed.html')
