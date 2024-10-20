from account.models import CustomUser as User
from django.forms import ModelForm


class UpdateClientForm(ModelForm):
    password = None

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name']
        exclude = ['password1', 'password2']
        labels = {
            'email': 'ایمیل',
            'first_name': 'نام',
            'last_name': 'نام خانوادگی'
        }
