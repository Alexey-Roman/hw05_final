from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.conf import settings

from .forms import PostForm, CommentForm
from .models import Post, Group, Follow

User = get_user_model()


def get_paginator(post_list, page_number):
    paginator = Paginator(post_list, settings.NUMBER_POSTS)
    return paginator.get_page(page_number)


def index(request):
    page_obj = get_paginator(
        Post.objects.select_related('author', 'group'),
        request.GET.get('page'),
    )
    template = 'posts/index.html'
    context = {
        'page_obj': page_obj,
    }
    return render(request, template, context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    page_obj = get_paginator(
        group.posts.select_related('author'),
        request.GET.get('page'),
    )
    template = 'posts/group_list.html'
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    page_obj = get_paginator(
        author.posts.select_related('group'),
        request.GET.get('page'),
    )
    following = (request.user.is_authenticated
                 and request.user.follower.filter(author=author).exists())
    template = 'posts/profile.html'
    context = {
        'page_obj': page_obj,
        'author': author,
        'following': following,
    }
    return render(request, template, context)


def post_detail(request, post_id):
    post = get_object_or_404(
        Post.objects.select_related('author', 'group'),
        id=post_id,
    )
    comments = post.comments.select_related('author')
    template = 'posts/post_detail.html'
    context = {
        'post': post,
        'comments': comments,
        'form': CommentForm(),
    }
    return render(request, template, context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None,
                    files=request.FILES or None, )
    if form.is_valid():
        create_post = form.save(commit=False)
        create_post.author = request.user
        create_post.save()
        return redirect('posts:profile', create_post.author)
    template = 'posts/create_post.html'
    context = {
        'form': form,
        'is_edit': False,
    }
    return render(request, template, context)


@login_required
def post_edit(request, post_id):
    edit_post = get_object_or_404(
        Post.objects.select_related('author', 'group'),
        id=post_id,
    )

    if request.user != edit_post.author:
        return redirect('posts:post_detail', post_id)
    form = PostForm(request.POST or None,
                    files=request.FILES or None,
                    instance=edit_post, )

    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id)
    template = 'posts/create_post.html'
    context = {
        'form': form,
        'is_edit': True,
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
def follow_index(request):
    page_obj = get_paginator(
        Post.objects.filter(
            author__following__user=request.user
        ).select_related('author', 'group'),
        request.GET.get('page'),
    )
    template = 'posts/follow.html'
    context = {
        'page_obj': page_obj,
    }
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if author != request.user:
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect('posts:profile', author)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    is_follower = Follow.objects.filter(user=request.user, author=author)
    if is_follower.exists():
        is_follower.delete()
    return redirect('posts:profile', username)
