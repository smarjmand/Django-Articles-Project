from django.db import models
from account.models import CustomUser as User


class Article(models.Model):
    title = models.CharField(max_length=100, verbose_name='عنوان مقاله')
    content = models.TextField(verbose_name='متن مقاله')
    date_posted = models.DateTimeField(auto_now_add=True, verbose_name='ایجاد شده دز')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, verbose_name='نویسنده')
    is_premium = models.BooleanField(default=False, verbose_name='مقاله ی ویژه')

    def __str__(self):
        name = f'{self.user.first_name} {self.user.last_name}'
        if self.is_premium:
            article_type = 'مقاله ویژه'
        else:
            article_type = 'مقاله عادی'
        return f'{self.title} / {name} / {article_type}'

    class Meta:
        verbose_name = 'مقاله'
        verbose_name_plural = 'مقالات'
