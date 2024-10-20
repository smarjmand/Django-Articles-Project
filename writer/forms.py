from .models import Article
from django.forms import ModelForm
from account.models import CustomUser as User


class ArticleForm(ModelForm):

    class Meta:
        model = Article
        fields = ['title', 'content', 'is_premium']


class UpdateWriterForm(ModelForm):

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
