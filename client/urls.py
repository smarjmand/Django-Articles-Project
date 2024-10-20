from django.urls import path
from . import views

urlpatterns = [
    path('dashboard', views.client_dashboard, name='client_dashboard_page'),
    path('articles', views.browse_articles, name='client_articles_page'),
    path('order-subscription', views.subscription, name='subscription_plans_page'),
    path('account', views.client_account, name='client_account_page'),
    path('delete-account', views.delete_account, name='client_delete_page'),
    path('payment-request/<plan>', views.payment_request, name='payment_request_view'),
    path('verify-payment', views.verify_payment, name='verify_payment_view'),
]