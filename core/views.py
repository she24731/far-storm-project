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
from django.views.decorators.csrf import csrf_exempt
import random
from .models import Category, Post, Bookmark, ExternalLink
from .forms import PostForm, UserRegistrationForm
from config.settings import CONTRIBUTOR_GROUP


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
    Public users see only approved posts.
    Contributors see approved posts + their own drafts/pending posts.
    Admins see all posts.
    """
    category = get_object_or_404(Category, slug=slug)
    posts = Post.objects.filter(category=category, status='approved').select_related('author', 'category')
    
    # Contributors can see approved posts + their own drafts/pending posts
    # Admins can see all posts
    if request.user.is_authenticated:
        user_groups = [g.name for g in request.user.groups.all()]
        if request.user.is_staff:
            # Admin: see all posts
            posts = Post.objects.filter(category=category).select_related('author', 'category')
        elif CONTRIBUTOR_GROUP in user_groups:
            # Contributor: see approved posts + own drafts/pending
            from django.db.models import Q
            posts = Post.objects.filter(
                category=category
            ).filter(
                Q(status='approved') | Q(author=request.user)
            ).select_related('author', 'category')
    
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
    Public users can only view approved posts.
    Contributors can view approved posts + their own drafts/pending posts.
    Admins can view all posts.
    """
    post = get_object_or_404(Post, slug=slug)
    
    # Check if user can view this post
    if post.status != 'approved':
        if not request.user.is_authenticated:
            messages.error(request, "This post is not available. Please log in.")
            return redirect('core:login')
        
        # Contributors can only see their own non-approved posts
        # Admins can see all posts
        user_groups = [g.name for g in request.user.groups.all()]
        if request.user.is_staff:
            # Admin can see all posts
            pass
        elif CONTRIBUTOR_GROUP in user_groups:
            # Contributor can only see their own non-approved posts
            if post.author != request.user:
                messages.error(request, "You can only view your own draft or pending posts.")
                return redirect('core:home')
        else:
            # Regular users cannot see non-approved posts
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
    
    TODO: Currently restricted to 'Contributors' group via @user_passes_test(is_contributor).
    The is_contributor function checks user.groups.filter(name='Contributors').exists().
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
@user_passes_test(is_contributor, login_url='core:home')
def contributor_post_list(request):
    """
    List all posts created by the current contributor.
    
    URL: /my-posts/
    Shows drafts, pending, approved, and rejected posts.
    """
    posts = Post.objects.filter(author=request.user).select_related('category').order_by('-updated_at')
    
    context = {
        'posts': posts,
    }
    return render(request, 'core/contributor_post_list.html', context)


@login_required
@user_passes_test(is_contributor, login_url='core:home')
def contributor_delete_post(request, post_id):
    """
    Delete a post (only own posts).
    
    URL: /my-posts/delete/<post_id>/
    """
    post = get_object_or_404(Post, id=post_id)
    
    # Only allow deleting own posts unless admin
    if post.author != request.user and not request.user.is_staff:
        messages.error(request, "You can only delete your own posts.")
        return redirect('core:contributor_post_list')
    
    if request.method == 'POST':
        post_title = post.title
        post.delete()
        messages.success(request, f'Post "{post_title}" has been deleted.')
        return redirect('core:contributor_post_list')
    
    context = {
        'post': post,
    }
    return render(request, 'core/contributor_delete_post.html', context)


@login_required
def bookmark_post(request, slug):
    """
    Toggle bookmark for a post.
    
    URL: /p/<slug>/bookmark/
    """
    post = get_object_or_404(Post, slug=slug)
    
    # Only allow bookmarking approved posts (or own posts for contributors)
    if post.status != 'approved' and post.author != request.user:
        messages.error(request, "You can only bookmark approved posts.")
        return redirect('core:post_detail', slug=post.slug)
    
    bookmark, created = Bookmark.objects.get_or_create(user=request.user, post=post)
    
    if created:
        messages.success(request, f'Post "{post.title}" has been bookmarked.')
    else:
        bookmark.delete()
        messages.info(request, f'Post "{post.title}" has been removed from bookmarks.')
    
    return redirect('core:post_detail', slug=post.slug)


@login_required
def bookmarks_list(request):
    """
    List all bookmarked posts for the current user.
    
    URL: /bookmarks/
    """
    bookmarks = Bookmark.objects.filter(user=request.user).select_related('post', 'post__category', 'post__author').order_by('-created_at')
    
    context = {
        'bookmarks': bookmarks,
    }
    return render(request, 'core/bookmarks_list.html', context)


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


# ============================================================================
# AUTHENTICATION VIEWS
# ============================================================================

def signup(request):
    """
    User registration view.
    
    Creates a new user account and automatically logs them in.
    New users are automatically assigned to the Contributor group.
    """
    if request.user.is_authenticated:
        # Redirect authenticated users away from signup page
        return redirect('core:home')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Assign user to Contributor group by default
            try:
                contributor_group = Group.objects.get(name=CONTRIBUTOR_GROUP)
                user.groups.add(contributor_group)
            except Group.DoesNotExist:
                # If Contributor group doesn't exist, create it
                contributor_group = Group.objects.create(name=CONTRIBUTOR_GROUP)
                user.groups.add(contributor_group)
            
            # Automatically log the user in after registration
            login(request, user)
            messages.success(request, f'Welcome, {user.username}! Your account has been created. You can now create posts!')
            return redirect('core:home')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'registration/signup.html', {'form': form})


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
    template_name = 'registration/logged_out.html'
    
    def dispatch(self, request, *args, **kwargs):
        messages.success(request, 'You have been successfully logged out.')
        return super().dispatch(request, *args, **kwargs)


# ============================================================================
# HEALTH CHECK ENDPOINT
# ============================================================================

def health_check(request):
    """
    Lightweight health check endpoint for monitoring.
    
    URL: /health/
    Returns JSON with status and database connectivity.
    Public endpoint, no authentication required.
    """
    try:
        # Perform a minimal database query to check connectivity
        Post.objects.exists()
        db_status = "ok"
        http_status = 200
    except Exception:
        db_status = "unreachable"
        http_status = 500
    
    response_data = {
        "status": "ok" if db_status == "ok" else "error",
        "db": db_status,
    }
    
    return JsonResponse(response_data, status=http_status)


def abtest_view(request):
    """
    A/B test endpoint for team far-storm.
    
    URL: /218b7ae/
    Publicly accessible, no authentication required.
    Shows team members and a button with variant text (kudos/thanks).
    
    A/B Test Logic:
    - Variant assignment: Random 50/50 split on first visit, persisted via cookie
    - Variant A: "kudos"
    - Variant B: "thanks"
    - Cookie name: "ab_variant" (30-day expiration)
    
    Debug Forcing (for manual QA only):
    - ?force_variant=a → always show "kudos"
    - ?force_variant=b → always show "thanks"
    - Forced variants are logged but marked as is_forced=True
    
    Server-side logging:
    - All variant exposures are logged to ABTestEvent model
    - Experiment name: "button_label_kudos_vs_thanks"
    """
    from .models import ABTestEvent
    
    # Team information
    team_nickname = "far-storm"
    team_members = [
        "Chun-Hung Yeh ( stormy-deer )",
        "Celine (Qijing) Li ( adorable-crow )",
        "Denise Wu ( super-giraffe )",
    ]
    
    experiment_name = "button_label_kudos_vs_thanks"
    is_forced = False
    
    # Debug forcing mechanism (for manual QA only)
    # Check URL parameter FIRST to override cookie
    force_param = request.GET.get('force_variant', '').strip().lower()
    cookie_variant = request.COOKIES.get('ab_variant')
    
    if force_param == 'a':
        variant = 'kudos'
        is_forced = True
    elif force_param == 'b':
        variant = 'thanks'
        is_forced = True
    else:
        # Normal A/B logic: check cookie only if no force parameter
        variant = cookie_variant
        
        if variant not in ['kudos', 'thanks']:
            # Randomly choose variant (50/50) if no cookie
            variant = random.choice(['kudos', 'thanks'])
    
    
    # Get session identifier (use cookie if available, otherwise use IP)
    session_id = request.COOKIES.get('ab_variant', '')
    if not session_id:
        # Generate a simple session ID from IP + user agent hash
        import hashlib
        session_data = f"{request.META.get('REMOTE_ADDR', '')}{request.META.get('HTTP_USER_AGENT', '')}"
        session_id = hashlib.md5(session_data.encode()).hexdigest()[:16]
    
    endpoint = '/218b7ae/'
    
    # Log variant exposure server-side (unless forced for QA)
    if not is_forced:
        try:
            ABTestEvent.objects.create(
                experiment_name=experiment_name,
                variant=variant,
                event_type=ABTestEvent.EVENT_TYPE_EXPOSURE,
                endpoint=endpoint,
                session_id=session_id,
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],  # Limit length
                user=request.user if request.user.is_authenticated else None,
                is_forced=False,
            )
        except Exception:
            # Silently fail if logging fails (don't break the page)
            pass
    
    # Prepare context
    context = {
        'team_nickname': team_nickname,
        'team_members': team_members,
        'variant': variant,
    }
    
    # Render template
    response = render(request, 'core/abtest.html', context)
    
    # Set cookie if it doesn't exist (30 days expiration)
    # Note: We still set cookie even for forced variants to maintain consistency
    if 'ab_variant' not in request.COOKIES or is_forced:
        # 30 days = 30 * 24 * 60 * 60 seconds
        max_age = 30 * 24 * 60 * 60
        response.set_cookie('ab_variant', variant, max_age=max_age, httponly=False)
    
    return response


@csrf_exempt
def abtest_click(request):
    """
    Endpoint to log A/B test button clicks (conversions) server-side.
    
    URL: /218b7ae/click/
    Called via AJAX when button is clicked.
    CSRF exempt since this is a public analytics endpoint.
    Logs as 'conversion' event type per specification.
    """
    from .models import ABTestEvent
    
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    variant = request.POST.get('variant', '')
    if variant not in ['kudos', 'thanks']:
        return JsonResponse({'error': 'Invalid variant'}, status=400)
    
    experiment_name = "button_label_kudos_vs_thanks"
    endpoint = '/218b7ae/'
    session_id = request.COOKIES.get('ab_variant', '')
    
    if not session_id:
        # Generate session ID similar to abtest_view
        import hashlib
        session_data = f"{request.META.get('REMOTE_ADDR', '')}{request.META.get('HTTP_USER_AGENT', '')}"
        session_id = hashlib.md5(session_data.encode()).hexdigest()[:16]
    
    try:
        ABTestEvent.objects.create(
            experiment_name=experiment_name,
            variant=variant,
            event_type=ABTestEvent.EVENT_TYPE_CONVERSION,
            endpoint=endpoint,
            session_id=session_id,
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
            user=request.user if request.user.is_authenticated else None,
            is_forced=False,
        )
        return JsonResponse({'status': 'logged'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)



