from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import ArticleForm, UpdateWriterForm
from .models import Article
from account.models import CustomUser as User


# ------------------------------------------------------------
# Writer Dashboard Page :
@login_required(login_url='login_page')
def writer_dashboard(request):
    return render(request, 'dashboard_writer.html')


# ------------------------------------------------------------
# To create a new article as a writer :
@login_required(login_url='login_page')
def create_article(request):

    form = ArticleForm()
    context = {'CreateArticleForm': form}

    if request.method == 'POST':
        form = ArticleForm(request.POST)
        if form.is_valid():
            article = form.save(commit=False)
            article.user = request.user
            article.save()
            return redirect('writer_articles_page')
        context = {'CreateArticleForm': form}

    return render(request, 'create_article.html', context)


# ------------------------------------------------------------
# To see all of the writer's articles :
@login_required(login_url='login_page')
def my_articles(request):

    current_user = request.user
    articles = Article.objects.filter(user=current_user)
    print(articles)
    context = {'AllArticles': articles}

    return render(request, 'my_articles.html', context)


# ------------------------------------------------------------
# To update an article :
@login_required(login_url='login_page')
def update_article(request, article_id):

    try:
        article = Article.objects.get(id=article_id, user=request.user)
    except Article.DoesNotExist:
        return redirect('writer_articles_page')

    form = ArticleForm(instance=article)
    context = {'UpdateArticleForm': form}

    if request.method == 'POST':
        form = ArticleForm(request.POST, instance=article)
        if form.is_valid():
            form.save()
            return redirect('writer_articles_page')
        context = {'UpdateArticleForm': form}

    return render(request, 'update_article.html', context)


# ------------------------------------------------------------
# To delete and article :
@login_required(login_url='login_page')
def delete_article(request, article_id):
    context = None
    try:
        article = Article.objects.get(id=article_id, user=request.user)
        context = {'article': article}
    except Article.DoesNotExist:
        return redirect('writer_articles_page')

    if request.method == 'POST':
        article.delete()
        return redirect('writer_articles_page')

    return render(request, 'delete_article.html', context)


# ------------------------------------------------------------
# To manage writer's account :
@login_required(login_url='login_page')
def account_management(request):

    form = UpdateWriterForm(instance=request.user)
    context = {'UpdateWriterAccountForm': form}

    if request.method == 'POST':
        form = UpdateWriterForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('writer_dashboard_page')
        context = {'UpdateWriterAccountForm': form}

    return render(request, 'account_management_writer.html', context)


# ------------------------------------------------------------
# To delete writer's account :
@login_required(login_url='login_page')
def delete_account(request):

    if request.method == 'POST':
        user = User.objects.get(email=request.user.email)
        user.delete()
        return redirect('login_page')

    return render(request, 'delete_account_writer.html')
