# - Import password reset token generator

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils import six
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.core.mail import send_mail
from django.conf import settings


# - Password reset token generator method

class UserVerificationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        user_id = six.text_type(user.pk)
        ts = six.text_type(timestamp)
        is_active = six.text_type(user.is_active)
        return f"{user_id}{ts}{is_active}"


user_tokenizer_generate = UserVerificationTokenGenerator()


def send_verification_email(user, domain):
    subject = 'فعال سازی حساب کاربری مقاله نو'
    message = render_to_string(
        'email_verification_link.html',
        {
            'user': user,
            'domain': domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': user_tokenizer_generate.make_token(user=user)
        }
    )
    user_email = user.email
    send_mail(
        subject,
        message,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[user_email]
    )
