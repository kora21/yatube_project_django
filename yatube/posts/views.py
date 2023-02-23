from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.views.decorators.cache import cache_page

from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect

from posts.models import Post
from posts.models import Group
from posts.models import User
from posts.models import Follow
from posts.forms import PostForm
from posts.forms import CommentForm


POSTS_PER_PAGE = 10


def get_page(request, post_list):
    paginator = Paginator(post_list, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


def index(request):
    title = "Это главная страница проекта Yatube"
    posts = Post.objects.all()
    page_obj = get_page(request, posts)
    context = {
        'title': title,
        'posts': posts,
        'groups': Group.objects.all(),
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    title = "Здесь будет информация о группах проекта Yatube"
    group = get_object_or_404(Group, slug=slug)
    posts = Post.objects.filter(group=group)
    page_obj = get_page(request, posts)
    context = {
        'title': title,
        'group': group,
        'posts': posts,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = author.posts.all()
    page_obj = get_page(request, author.posts.all())
    context = {
        'author': author,
        'posts': posts,
        'page_obj': page_obj,
    }
    if not request.user.is_anonymous:
        following = Follow.objects.filter(user=request.user,
                                          author=author).exists()
        context["following"] = following
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm()
    comment = post.comments.select_related('author').all()
    context = {
        'post': post,
        'comment': comment,
        'form': form,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None,
                    files=request.FILES or None)
    if not request.method == "POST":
        return render(request, "posts/post_create.html", {"form": form})
    if not form.is_valid():
        return render(request, 'posts/post_create.html', {'form': form})
    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect('posts:profile', request.user.username)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id=post_id)
    form = PostForm(request.POST or None,
                    files=request.FILES or None,
                    instance=post)
    if form.is_valid():
        post = form.save(commit=False)
        post.author == request.user
        post.save()
        return redirect('posts:post_detail', post_id=post_id)
    context = {'post': post,
               'form': form,
               'is_edit': True}
    return render(request, 'posts/post_create.html', context)


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
    post_list = Post.objects.select_related('author', 'group')
    page_obj = get_page(request, post_list)
    context = {
        'post_list': post_list,
        'page_obj': page_obj,
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if request.user != author:
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    Follow.objects.filter(
        user=request.user, author__username=username).delete()
    return redirect('posts:profile', username=username)


@cache_page(20)
def my_view(request):
    posts = Post.objects.select_related('author', 'group').all()
    page_obj = get_page(request, posts)
    context = {
        'page_obj': page_obj
    }
    return render(request, 'posts/index.html', context)
