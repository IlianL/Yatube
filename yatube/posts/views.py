from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from .forms import PostForm, CommentForm
from .models import Group, Post, Follow
from .utils import get_page

User = get_user_model()


@cache_page(20, key_prefix='index_page')
def index(request):
    """Главная страница."""
    template = 'posts/index.html'
    page_obj = get_page(request, Post.objects.all())
    context = {
        'page_obj': page_obj,
    }
    return render(request, template, context)


def group_posts(request, slug):
    """Страница определённой группы."""
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    page_obj = get_page(request, group.posts.all())
    context = {
        'page_obj': page_obj,
        'group': group
    }
    return render(request, template, context)


def profile(request, username):
    """Страница профиля юзера."""
    template = 'posts/profile.html'
    author = get_object_or_404(User, username=username)
    user = request.user
    page_obj = get_page(request, author.posts.all())
    following = (
        user.is_authenticated
        and Follow.objects.filter(user=user, author=author)
    )
    context = {
        'page_obj': page_obj,
        'author': author,
        'following': following
    }
    return render(request, template, context)


def post_detail(request, post_id):
    """Подробная информация о посте"""
    template = 'posts/post_detail.html'
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm()
    comments = post.comments.all()
    context = {
        'form': form,
        'post': post,
        'comments': comments
    }
    return render(request, template, context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def post_create(request):
    """Создание нового поста."""
    template = 'posts/create_or_update_post.html'
    is_edit = False
    title = 'Новый пост'
    form = PostForm(
        request.POST or None,
        files=request.FILES or None
    )
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        form.save()
        return redirect('posts:profile', request.user.username)
    return render(request, template,
                  {'title': title, 'form': form, 'is_edit': is_edit})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    is_edit = True
    template = 'posts/create_or_update_post.html'
    title = 'Редактировать запись'
    if request.user != post.author:
        return redirect('posts:post_detail', post_id=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id)
    return render(request, template, {
        'form': form, 'post': post,
        'title': title, 'is_edit': is_edit
    })


@login_required
def follow_index(request):
    template = 'posts/follow.html'
    posts = Post.objects.filter(
        author__following__user=request.user)
    page_obj = get_page(request, posts)
    context = {'page_obj': page_obj}
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    user_followed = Follow.objects.filter(
        user=request.user, author=author
    ).exists()
    if author != request.user and not user_followed:
        Follow.objects.create(user=request.user, author=author)
    return redirect('posts:profile', author)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    if request.user != author:
        Follow.objects.filter(user=request.user, author=author).delete()
    return redirect("posts:profile", username=username)
