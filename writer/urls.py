from django.urls import path
from . import views

urlpatterns = [
    path('dashboard', views.writer_dashboard, name='writer_dashboard_page'),
    path('create-article', views.create_article, name='create_article_page'),
    path('my-articles', views.my_articles, name='writer_articles_page'),
    path('update-article/<int:article_id>', views.update_article, name='update_article_page'),
    path('delete-article/<int:article_id>', views.delete_article, name='delete_article_page'),
    path('account', views.account_management, name='writer_account_page'),
    path('delete-account', views.delete_account, name='delete_account_writer')

]
