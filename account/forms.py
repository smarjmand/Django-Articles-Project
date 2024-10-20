from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm
from .models import CustomUser as User


class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'password1', 'password2', 'is_writer']
        labels = {
            'email': 'ایمیل',
            'first_name': 'نام',
            'last_name': 'نام خانوادگی',
            'password1': 'گذرواژه',
            'password2': 'تکرار گذرواژه'
        }
        help_texts = {
            'password1': None,
            'password2': None
        }

    # To change labels and help_texts to farsi :
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for k, v in self.Meta.labels.items():
            self[k].label = v
        for k, v in self.Meta.help_texts.items():
            self[k].help_text = v
