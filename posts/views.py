from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User


def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, 10)
    # Из URL извлекаем номер запрошенной страницы - это значение параметра page
    page_number = request.GET.get("page")
    # Получаем набор записей для страницы с запрошенным номером
    page = paginator.get_page(page_number)
    return render(request, "posts/index.html", {"page": page, })


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return render(request, "posts/group.html", {"group": group, "page": page})


@login_required
def new_post(request):
    form = PostForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        new_post = form.save(commit=False)
        new_post.author = request.user
        new_post.save()
        return redirect("posts:index")
    return render(request, "posts/new_post.html", {"form": form})


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = author.posts.all()
    post_count = post_list.count()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    if request.user.username:
        following = Follow.objects.filter(user=request.user,
                                          author=author).exists()
    else:
        following = False
    followers = author.following.all().count()
    followings = author.follower.all().count()
    return render(
        request,
        "posts/profile.html",
        {"author": author,
         "page": page,
         "post_count": post_count,
         "following": following,
         "followers": followers,
         "followings": followings}
    )


def post_view(request, username, post_id):
    post = get_object_or_404(Post, id=post_id, author__username=username)
    form = CommentForm()
    author = post.author
    comments = post.comments.all()
    post_list = author.posts.all()
    post_count = post_list.count()
    if request.user.username:
        following = Follow.objects.filter(user=request.user,
                                          author=author).exists()
    else:
        following = False
    followers = author.following.all().count()
    followings = author.follower.all().count()
    return render(
        request,
        "posts/post.html",
        {"author": author,
         "form": form,
         "post": post,
         "post_count": post_count,
         "comments": comments,
         "following": following,
         "followers": followers,
         "followings": followings})


@login_required
def post_edit(request, username, post_id):
    # Запрещаем другим авторам попасть на страницу редактирования
    editable_post = get_object_or_404(Post, id=post_id)
    if request.user != editable_post.author:
        return redirect("posts:post", username=username, post_id=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=editable_post)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("posts:post", username=username, post_id=post_id)
    return render(
        request,
        "posts/new_post.html",
        {"form": form,
         "post": editable_post})


@login_required
def new_post(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if request.method == "POST" and form.is_valid():
        new_post = form.save(commit=False)
        new_post.author = request.user
        new_post.save()
        return redirect("posts:index")
    return render(
        request,
        "posts/new_post.html",
        {"form": form})


def page_not_found(request, exception):
    # Переменная exception содержит отладочную информацию,
    # выводить её в шаблон пользователской страницы 404 мы не станем
    return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=404
    )


def server_error(request):
    return render(request, "misc/500.html", status=500)


@login_required
def add_comment(request, username, post_id):
    form = CommentForm(request.POST or None)
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.all()
    author = post.author
    if request.method == "POST" and form.is_valid():
        new_comment = form.save(commit=False)
        new_comment.post = post
        new_comment.author = request.user
        new_comment.save()
        return redirect("posts:post",
                        username=username, post_id=post_id)
    return render(request, "posts/comments.html",
                  {"form": form,
                   "comments": comments,
                   "author": author,
                   "post": post})


@login_required
def follow_index(request):
    # информация о текущем пользователе доступна в переменной request.user
    user = get_object_or_404(User, username=request.user)
    # фильтруем посты по принадлежности избранным авторам и сортируем
    post_list = Post.objects.filter(
        author__following__user=user).order_by("-pub_date")
    paginator = Paginator(post_list, 10)
    # Из URL извлекаем номер запрошенной страницы - это значение параметра page
    page_number = request.GET.get("page")
    # Получаем набор записей для страницы с запрошенным номером
    page = paginator.get_page(page_number)

    return render(request, "posts/follow.html", {"page": page})


@login_required
def profile_follow(request, username):
    # Подписка на автора
    author = get_object_or_404(User, username=username)
    user = request.user
    if author != user:
        Follow.objects.get_or_create(user=user, author=author)
    return redirect("posts:profile", username=username)


@login_required
def profile_unfollow(request, username):
    # Отписка от автора
    author = get_object_or_404(User, username=username)
    Follow.objects.filter(author=author, user=request.user).delete()
    return redirect("posts:profile", username=username)
