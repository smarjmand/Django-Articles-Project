from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from writer.models import Article
from .models import Subscription
from .forms import UpdateClientForm
from account.models import CustomUser as User
from django.conf import settings
from django.http import HttpResponse, HttpRequest
import requests
import json


# ------------------------------------------------------------
# To show client dashboard page :
@login_required(login_url='login_page')
def client_dashboard(request):
    msg = None
    order = None
    try:
        subscription = Subscription.objects.get(user=request.user, is_active=True)
        if subscription.premium_subscription is True:
            msg = '⭐️ اشتراک ویژه'
        else:
            msg = '🔓 اشتراک معمولی'
    except Subscription.DoesNotExist:
        msg = '🔒 برای مشاهده ی مقاله ها خرید اشتراک الزامی است 🔒'
        order = True

    context = {'msg': msg, 'order': order}
    return render(request, 'dashboard_client.html', context)


# ------------------------------------------------------------
# To read articles :
@login_required(login_url='login_page')
def browse_articles(request):

    try:
        subscription = Subscription.objects.get(user=request.user, is_active=True)
    except Subscription.DoesNotExist:
        context = {
            'title': 'مشاهده مقالات',
            'head_line': 'عدم دسترسی',
            'msg': 'برای مشاهده مقالات ابتدا اشتراک خریداری فرمایید'
        }
        return render(request, 'messages_client.html', context)

    if subscription.premium_subscription is True:
        articles = Article.objects.all()
    else:
        articles = Article.objects.all().filter(is_premium=False)

    context = {'AllArticles': articles}
    return render(request, 'browse_articles.html', context)


# ------------------------------------------------------------
# To buy subscription :
@login_required(login_url='login_page')
def subscription(request):
    return render(request, 'order_subscription.html')


# ------------------------------------------------------------
# Client account management :
@login_required(login_url='login_page')
def client_account(request):
    form = UpdateClientForm(instance=request.user)

    try:
        sub_plan = Subscription.objects.get(user=request.user)
        plan = True
    except Subscription.DoesNotExist:
        plan = False

    context = {'UpdateClientAccountForm': form, 'plan': plan}

    if request.method == 'POST':
        form = UpdateClientForm(data=request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('client_dashboard_page')
        context = {'UpdateClientAccountForm': form, 'plan': plan}

    return render(request, 'account_management_client.html', context)


# ------------------------------------------------------------
# To delete client account :
def delete_account(request):

    if request.method == 'POST':
        user = User.objects.get(email=request.user.email)
        user.delete()
        return redirect('login_page')

    return render(request, 'delete_account_client.html')


# ------------------------------------------------------------
# To buy subscription from ZarrinPal ( sending request ) :
@login_required(login_url='login_page')
def payment_request(request: HttpRequest, plan):
    plan_options = {
        'standard': {'amount': 500000, 'description': 'خرید اشتراک استاندارد'},
        'premium': {'amount': 1000000, 'description': 'خرید اشتراک ویژه'}
    }

    if plan in plan_options:
        amount = plan_options[plan]['amount']
        description = plan_options[plan]['description']
    else:
        amount = 0
        description = 'نامعتبر'

    name = f'{request.user.first_name} {request.user.last_name}'
    obj, created = Subscription.objects.get_or_create(
        subscriber_name=name,
        subscription_cost=amount,
        user=request.user,
        premium_subscription=True if plan == 'premium' else False
    )

    req_data = {
        "merchant_id": settings.MERCHANT,
        "amount": amount,
        "callback_url": 'http://127.0.0.1:8080/client/verify-payment',
        "description": description
    }

    req_header = {"accept": "application/json", "content-type": "application/json'"}
    req = requests.post(url=settings.ZP_API_REQUEST, data=json.dumps(req_data), headers=req_header)
    authority = req.json()['data']['authority']
    if len(req.json()['errors']) == 0:
        return redirect(settings.ZP_API_STARTPAY.format(authority=authority))
    else:
        e_code = req.json()['errors']['code']
        e_message = req.json()['errors']['message']
        context = {
            'title': 'نتیجه پرداخت',
            'head_line': 'پرداخت موفق',
            'msg': e_message
        }
        return render(request, 'messages_client.html', context)


# ------------------------------------------------------------
# To get response from ZarrinPal
@login_required(login_url='login_page')
def verify_payment(request: HttpRequest):
    t_authority = request.GET['Authority']
    if request.GET.get('Status') == 'OK':
        req_header = {"accept": "application/json", "content-type": "application/json'"}
        try:
            sub_detail = Subscription.objects.get(user=request.user)
        except Subscription.DoesNotExist:
            raise 404

        req_data = {
            "merchant_id": settings.MERCHANT,
            "amount": sub_detail.subscription_cost,
            "authority": t_authority
        }
        req = requests.post(url=settings.ZP_API_VERIFY, data=json.dumps(req_data), headers=req_header)
        if len(req.json()['errors']) == 0:
            t_status = req.json()['data']['code']
            if t_status == 100:
                sub_detail.is_active = True
                sub_detail.payment_subscription_id = req.json()['data']['ref_id']
                sub_detail.save()
                context = {
                    'title': 'نتیجه پرداخت',
                    'head_line': 'پرداخت موفق',
                    'msg': 'اشتراک شما با موفقیت ایجاد شد'
                }
                return render(request, 'messages_client.html', context)
            elif t_status == 101:
                context = {
                    'title': 'نتیجه پرداخت',
                    'head_line': 'تراکنش تکراری',
                    'msg': 'این تراکنش قبلا ثبت شده است'
                }
                return render(request, 'messages_client.html', context)
            else:
                context = {
                    'title': 'نتیجه پرداخت',
                    'head_line': 'تراکنش ناموفق',
                    'msg': str(req.json()['data']['message'])
                }
                return render(request, 'messages_client.html', context)
        else:
            e_message = req.json()['errors']['message']
            context = {
                'title': 'نتیجه پرداخت',
                'head_line': 'تراکنش ناموفق',
                'msg': e_message
            }
            return render(request, 'messages_client.html', context)
    else:
        context = {
            'title': 'نتیجه پرداخت',
            'head_line': 'تراکنش ناموفق',
            'msg': 'پرداخت با خطا مواجه شد / کاربر از پرداخت ممانعت کرد'
        }
        return render(request, 'messages_client.html', context)


