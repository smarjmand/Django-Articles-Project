from django.db import models
from account.models import CustomUser as User


class Subscription(models.Model):
    subscriber_name = models.CharField(max_length=100, verbose_name='نام مشتری')
    subscription_cost = models.IntegerField(verbose_name='قیمت اشتراک')
    payment_subscription_id = models.CharField(max_length=300, blank=True, verbose_name='شناسه پرداخت')
    user = models.OneToOneField(User, on_delete=models.CASCADE, unique=True, verbose_name='کاربر در سایت')
    premium_subscription = models.BooleanField(default=False, verbose_name='اشتراک ویژه')
    is_active = models.BooleanField(default=False, verbose_name='فعال')

    def __str__(self):
        msg = ''
        if self.premium_subscription is True:
            msg = ' / اشتراک ویژه'
        return f'{self.subscriber_name} {msg}'

    class Meta:
        verbose_name = 'اشتراک'
        verbose_name_plural = 'اشتراک ها'
