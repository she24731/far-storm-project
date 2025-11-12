"""
Views for Yale Newcomer Survival Guide.

Handles all HTTP requests and responses.
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.models import Group
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from django.http import JsonResponse
from .models import Category, Post, Bookmark, ExternalLink
from .forms import PostForm
from config.settings import READER_GROUP, CONTRIBUTOR_GROUP, ADMIN_GROUP


def is_contributor(user):
    """Check if user is in Contributor group."""
    return user.is_authenticated and user.groups.filter(name=CONTRIBUTOR_GROUP).exists()


def is_admin(user):
    """Check if user is staff/admin."""
    return user.is_authenticated and user.is_staff


def home(request):
    """
    Home page: category hub + latest approved posts.
    
    Shows all categories and the 5 most recent approved posts.
    """
    categories = Category.objects.all()
    latest_posts = Post.objects.filter(status='approved').select_related('category', 'author')[:5]
    
    # Simple search functionality
    query = request.GET.get('q', '').strip()
    if query:
        latest_posts = Post.objects.filter(
            Q(title__icontains=query) | Q(content__icontains=query),
            status='approved'
        ).select_related('category', 'author')[:10]
    
    context = {
        'categories': categories,
        'latest_posts': latest_posts,
        'query': query,
    }
    return render(request, 'core/home.html', context)


def category_list(request, slug):
    """
    Category listing page showing approved posts in a category.
    
    URL: /c/<slug>/
    """
    category = get_object_or_404(Category, slug=slug)
    posts = Post.objects.filter(category=category, status='approved').select_related('author', 'category')
    
    # Contributors and Admins can see pending/draft posts
    if request.user.is_authenticated:
        user_groups = [g.name for g in request.user.groups.all()]
        if CONTRIBUTOR_GROUP in user_groups or request.user.is_staff:
            posts = Post.objects.filter(category=category).select_related('author', 'category')
    
    external_links = ExternalLink.objects.filter(category=category)
    
    context = {
        'category': category,
        'posts': posts,
        'external_links': external_links,
    }
    return render(request, 'core/category_list.html', context)


def post_detail(request, slug):
    """
    Post detail page.
    
    URL: /p/<slug>/
    Only approved posts visible to readers.
    """
    post = get_object_or_404(Post, slug=slug)
    
    # Check if user can view this post
    if post.status != 'approved':
        if not request.user.is_authenticated:
            return redirect('core:login')
        
        user_groups = [g.name for g in request.user.groups.all()]
        if CONTRIBUTOR_GROUP not in user_groups and not request.user.is_staff:
            messages.error(request, "This post is not available.")
            return redirect('core:home')
    
    # Check if bookmarked
    is_bookmarked = False
    if request.user.is_authenticated:
        is_bookmarked = Bookmark.objects.filter(user=request.user, post=post).exists()
    
    context = {
        'post': post,
        'is_bookmarked': is_bookmarked,
    }
    return render(request, 'core/post_detail.html', context)


@login_required
@user_passes_test(is_contributor, login_url='core:home')
def submit_post(request, post_id=None):
    """
    Contributor submit/edit post view.
    
    URL: /submit/ or /submit/<post_id>/
    Contributors can create drafts or submit for review (pending).
    """
    post = None
    if post_id:
        post = get_object_or_404(Post, id=post_id)
        # Only allow editing own posts unless admin
        if post.author != request.user and not request.user.is_staff:
            messages.error(request, "You can only edit your own posts.")
            return redirect('core:home')
    
    if request.method == 'POST':
        form = PostForm(request.POST, instance=post, user=request.user)
        if form.is_valid():
            post = form.save(commit=False)
            if not post.author_id:
                post.author = request.user
            post.save()
            
            if post.status == 'pending':
                messages.success(request, f'Post "{post.title}" submitted for review.')
            else:
                messages.success(request, f'Post "{post.title}" saved as draft.')
            
            return redirect('core:post_detail', slug=post.slug)
    else:
        form = PostForm(instance=post, user=request.user)
    
    context = {
        'form': form,
        'post': post,
    }
    return render(request, 'core/submit_post.html', context)


@login_required
@user_passes_test(is_admin, login_url='core:home')
def dashboard(request):
    """
    Admin dashboard for reviewing pending posts.
    
    URL: /dashboard/
    Admins can approve or reject pending posts.
    """
    pending_posts = Post.objects.filter(status='pending').select_related('author', 'category').order_by('-updated_at')
    draft_posts = Post.objects.filter(status='draft').select_related('author', 'category').order_by('-updated_at')
    
    context = {
        'pending_posts': pending_posts,
        'draft_posts': draft_posts,
    }
    return render(request, 'core/dashboard.html', context)


@login_required
@user_passes_test(is_admin, login_url='core:home')
def approve_post(request, post_id):
    """Approve a pending post."""
    post = get_object_or_404(Post, id=post_id)
    post.status = 'approved'
    post.published_at = timezone.now()
    post.save()
    messages.success(request, f'Post "{post.title}" has been approved.')
    return redirect('core:dashboard')


@login_required
@user_passes_test(is_admin, login_url='core:home')
def reject_post(request, post_id):
    """Reject a pending post."""
    post = get_object_or_404(Post, id=post_id)
    post.status = 'rejected'
    post.save()
    messages.success(request, f'Post "{post.title}" has been rejected.')
    return redirect('core:dashboard')


# Authentication views
class CustomLoginView(LoginView):
    """Custom login view."""
    template_name = 'registration/login.html'
    
    def get_success_url(self):
        user = self.request.user
        if user.is_staff:
            messages.success(self.request, f'Welcome back, {user.username}! (Admin)')
        elif is_contributor(user):
            messages.success(self.request, f'Welcome back, {user.username}! (Contributor)')
        else:
            messages.success(self.request, f'Welcome back, {user.username}! (Reader)')
        return super().get_success_url()


class CustomLogoutView(LogoutView):
    """Custom logout view."""
    def dispatch(self, request, *args, **kwargs):
        messages.success(request, 'You have been successfully logged out.')
        return super().dispatch(request, *args, **kwargs)

