"""
Views for the Yale Newcomer Survival Guide application.

This module handles HTTP requests and returns appropriate responses
for home page, category listings, post details, search functionality,
and authentication (login, signup, logout).
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.models import Group
from django.contrib import messages
from django.db.models import Q
from .models import Category, Post, ExternalLink, Bookmark
from .forms import UserRegistrationForm
from yale_newcomer_survival_guide.settings import READER_GROUP, CONTRIBUTOR_GROUP, ADMIN_GROUP


def home(request):
    """
    Home page view displaying all categories.
    
    Shows a hub of all available categories that users can browse.
    """
    categories = Category.objects.all()
    context = {
        'categories': categories,
    }
    return render(request, 'guide/home.html', context)


def category_detail(request, slug):
    """
    Category detail view showing all posts in a category.
    
    - Readers: see only approved posts
    - Contributors/Admins: see all posts (including pending/draft)
    """
    category = get_object_or_404(Category, slug=slug)
    
    # Base queryset - only approved posts for regular users
    posts = Post.objects.filter(category=category, status='approved').select_related('author', 'category')
    
    # Contributors and Admins can see all posts
    if request.user.is_authenticated:
        user_groups = [g.name for g in request.user.groups.all()]
        if CONTRIBUTOR_GROUP in user_groups or ADMIN_GROUP in user_groups:
            posts = Post.objects.filter(category=category).select_related('author', 'category')
    
    # Get external links for this category
    external_links = ExternalLink.objects.filter(category=category)
    
    context = {
        'category': category,
        'posts': posts,
        'external_links': external_links,
    }
    return render(request, 'guide/category_detail.html', context)


def post_detail(request, slug):
    """
    Post detail view showing a single post.
    
    - Only approved posts visible to readers
    - Contributors/Admins can see pending/draft posts
    """
    post = get_object_or_404(Post, slug=slug)
    
    # Check if user can view this post
    if post.status != 'approved':
        if not request.user.is_authenticated:
            return redirect('guide:login')
        
        user_groups = [g.name for g in request.user.groups.all()]
        if CONTRIBUTOR_GROUP not in user_groups and ADMIN_GROUP not in user_groups:
            messages.error(request, "This post is not available.")
            return redirect('guide:home')
    
    # Check if post is bookmarked by current user
    is_bookmarked = False
    if request.user.is_authenticated:
        is_bookmarked = Bookmark.objects.filter(user=request.user, post=post).exists()
    
    context = {
        'post': post,
        'is_bookmarked': is_bookmarked,
    }
    return render(request, 'guide/post_detail.html', context)


def search(request):
    """
    Search view for finding posts and categories.
    
    Searches in post titles, content, and category names.
    """
    query = request.GET.get('q', '').strip()
    results = {
        'posts': [],
        'categories': [],
    }
    
    if query:
        # Search posts (only approved for regular users)
        post_query = Q(title__icontains=query) | Q(content__icontains=query) | Q(summary__icontains=query)
        posts = Post.objects.filter(post_query, status='approved').select_related('category', 'author')
        
        # Contributors/Admins can see all posts in search
        if request.user.is_authenticated:
            user_groups = [g.name for g in request.user.groups.all()]
            if CONTRIBUTOR_GROUP in user_groups or ADMIN_GROUP in user_groups:
                posts = Post.objects.filter(post_query).select_related('category', 'author')
        
        results['posts'] = posts
        
        # Search categories
        results['categories'] = Category.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )
    
    context = {
        'query': query,
        'results': results,
    }
    return render(request, 'guide/search.html', context)


@login_required
def toggle_bookmark(request, post_slug):
    """
    Toggle bookmark for a post.
    
    Creates a bookmark if it doesn't exist, removes it if it does.
    """
    post = get_object_or_404(Post, slug=post_slug)
    bookmark, created = Bookmark.objects.get_or_create(user=request.user, post=post)
    
    if not created:
        # Bookmark already exists, remove it
        bookmark.delete()
        messages.success(request, f'Removed "{post.title}" from bookmarks.')
    else:
        messages.success(request, f'Bookmarked "{post.title}".')
    
    return redirect('guide:post_detail', slug=post_slug)


# ============================================================================
# AUTHENTICATION VIEWS
# ============================================================================

def signup(request):
    """
    User registration view with automatic Reader group assignment.
    
    New users are automatically assigned to the Reader group upon registration.
    After successful registration, users are automatically logged in.
    """
    if request.user.is_authenticated:
        # Redirect authenticated users away from signup page
        return redirect('guide:home')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            # Create the user
            user = form.save()
            
            # Assign user to Reader group by default
            try:
                reader_group = Group.objects.get(name=READER_GROUP)
                user.groups.add(reader_group)
            except Group.DoesNotExist:
                # If Reader group doesn't exist, create it
                reader_group = Group.objects.create(name=READER_GROUP)
                user.groups.add(reader_group)
            
            # Log the user in automatically after registration
            login(request, user)
            messages.success(
                request, 
                f'Welcome, {user.username}! Your account has been created successfully. You have been assigned the Reader role.'
            )
            return redirect('guide:home')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'guide/signup.html', {'form': form})


class CustomLoginView(LoginView):
    """
    Custom login view with template and role-based redirect.
    
    After login, users are redirected based on their role:
    - Readers: Home page
    - Contributors/Admins: Home page (with additional options)
    """
    template_name = 'guide/login.html'
    
    def get_success_url(self):
        """Redirect based on user role after successful login."""
        user = self.request.user
        user_groups = [g.name for g in user.groups.all()]
        
        if ADMIN_GROUP in user_groups:
            messages.success(self.request, f'Welcome back, {user.username}! (Admin)')
        elif CONTRIBUTOR_GROUP in user_groups:
            messages.success(self.request, f'Welcome back, {user.username}! (Contributor)')
        else:
            messages.success(self.request, f'Welcome back, {user.username}! (Reader)')
        
        return super().get_success_url()


class CustomLogoutView(LogoutView):
    """
    Custom logout view with success message.
    """
    def dispatch(self, request, *args, **kwargs):
        """Add success message before logout."""
        messages.success(request, 'You have been successfully logged out.')
        return super().dispatch(request, *args, **kwargs)

