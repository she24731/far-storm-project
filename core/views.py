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
from django.http import JsonResponse, HttpResponseNotAllowed, HttpRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.decorators.cache import never_cache
from django.views.decorators.vary import vary_on_headers
import random
from .models import Category, Post, Bookmark, ExternalLink
from .forms import PostForm, UserRegistrationForm
from config.settings import CONTRIBUTOR_GROUP


# Helper functions for A/B test session keys
def _ab_session_variant_key(experiment_name: str) -> str:
    """Generate session key for storing variant assignment."""
    return f"abexp:{experiment_name}:variant"


def _ab_session_exposed_key(experiment_name: str, endpoint: str) -> str:
    """Generate session key for tracking exposure per experiment+endpoint."""
    return f"abexp:{experiment_name}:exposed:{endpoint}"


def is_bot_request(request: HttpRequest) -> bool:
    """Strict fail-closed bot detection."""
    ua = (request.META.get("HTTP_USER_AGENT") or "").lower()
    
    # No UA = treat as bot
    if not ua:
        return True
    
    # Must look like a real browser
    browser_signatures = ["chrome", "safari", "firefox", "edg", "opr"]
    if "mozilla" not in ua or not any(sig in ua for sig in browser_signatures):
        return True
    
    # Known bot/monitor/HTTP client signatures
    bot_keywords = [
        "bot", "spider", "crawler", "scraper",
        "render", "uptime", "health", "monitor",
        "pingdom", "statuscake", "github", "gitlab",
        "curl", "python-requests", "httpclient", "go-http-client",
    ]
    if any(k in ua for k in bot_keywords):
        return True
    
    return False


def _is_navigation_request(request: HttpRequest) -> bool:
    """Check if request is a real navigation (not prefetch/background)."""
    dest = (request.META.get("HTTP_SEC_FETCH_DEST") or "").lower()
    mode = (request.META.get("HTTP_SEC_FETCH_MODE") or "").lower()
    site = (request.META.get("HTTP_SEC_FETCH_SITE") or "").lower()
    
    if not dest or not mode or not site:
        return False
    
    if dest not in {"document", "iframe"}:
        return False
    
    if mode != "navigate":
        return False
    
    if site not in {"same-origin", "none"}:
        return False
    
    return True


def _is_click_request(request: HttpRequest) -> bool:
    """Check if request is a real click (not background fetch)."""
    mode = (request.META.get("HTTP_SEC_FETCH_MODE") or "").lower()
    site = (request.META.get("HTTP_SEC_FETCH_SITE") or "").lower()
    
    if not mode or not site:
        return False
    
    if site != "same-origin":
        return False
    
    if mode not in {"cors", "same-origin"}:
        return False
    
    return True


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


@never_cache
@vary_on_headers("Cookie")
def abtest_view(request):
    """
    A/B test page view.

    Behavior:
    - GET only.
    - On first real browser visit per session: assign variant + log ONE Exposure.
    - On reloads in the same session: do NOT log additional Exposure.
    
    This view only handles /218b7ae/ - any other path should not reach here.
    """
    from django.http import Http404
    from .models import ABTestEvent
    
    # Safety check: ensure we're on the correct path (defense against URL routing bugs)
    if request.path != '/218b7ae/':
        raise Http404("A/B test endpoint not found")
    
    if request.method != "GET":
        return HttpResponseNotAllowed(["GET"])
    
    experiment_name = "button_label_kudos_vs_thanks"
    endpoint = "/218b7ae/"
    session_key_variant = f"abexp:{experiment_name}:variant"
    session_key_exposed = f"abexp:{experiment_name}:exposed:{endpoint}"
    
    # Ensure we have a session
    if not request.session.session_key:
        request.session.save()
    session_id = request.session.session_key
    
    # Real user filtering: only count genuine top-level navigations
    ua = (request.META.get("HTTP_USER_AGENT") or "").lower()
    accept = (request.META.get("HTTP_ACCEPT") or "").lower()
    sec_fetch_mode = request.META.get("HTTP_SEC_FETCH_MODE", "").lower()
    
    # Conservative bot filtering: require browser UA, exclude known bots
    is_browser_ua = (
        ua
        and "mozilla" in ua
        and not any(bad in ua for bad in ["bot", "spider", "crawler", "curl", "python", "uptime", "httpclient"])
    )
    
    # Real navigation check: Sec-Fetch-Mode == "navigate" OR (no Sec-Fetch but Accept contains text/html) OR (no Sec-Fetch and no Accept - fallback for tests/older browsers)
    is_real_navigation = (
        request.method == "GET"
        and is_browser_ua
        and (
            sec_fetch_mode == "navigate"
            or (not sec_fetch_mode and "text/html" in accept)
            or (not sec_fetch_mode and not accept)  # Fallback for tests/older browsers
        )
    )
    
    # 1) Assign variant once per session (50/50 split)
    variant = request.session.get(session_key_variant)
    if not variant:
        variant = random.choice(["kudos", "thanks"])
        request.session[session_key_variant] = variant
        request.session.modified = True
    
    # 2) Log ONE exposure on first real browser page load
    if is_real_navigation and not request.session.get(session_key_exposed):
        ABTestEvent.objects.get_or_create(
            experiment_name=experiment_name,
            event_type=ABTestEvent.EVENT_TYPE_EXPOSURE,
            endpoint=endpoint,
            session_id=session_id,
            defaults={"variant": variant},
        )
        request.session[session_key_exposed] = True
        request.session.modified = True
    
    # Team information for display
    team_members = [
        "Chun-Hung Yeh ( stormy-deer )",
        "Celine (Qijing) Li ( adorable-crow )",
        "Denise Wu ( super-giraffe )",
    ]
    
    # 3) Render page
    response = render(
        request,
        "core/abtest.html",
        {
            "variant": variant,
            "experiment_name": experiment_name,
            "endpoint_hash": "218b7ae",
            "team_members": team_members,
        },
    )
    
    # Extra hardening: ensure no caching (some proxies/CDNs ignore decorators)
    response["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response["Pragma"] = "no-cache"
    response["Expires"] = "0"
    response["Vary"] = "Cookie"
    
    return response


@csrf_exempt
@require_POST
@never_cache
@vary_on_headers("Cookie")
def abtest_click(request):
    """
    A/B test click handler.

    Behavior:
    - POST only.
    - Logs Conversion on every click.
    - Backfills exposure if missing (only once).
    - Variant comes from session only (NOT from POST body).
    
    This view only handles /218b7ae/click/ - any other path should not reach here.
    
    Cache-Control headers prevent intermediaries from caching conversion responses.
    """
    from django.http import Http404
    from .models import ABTestEvent
    
    # Safety check: ensure we're on the correct path (defense against URL routing bugs)
    if request.path != '/218b7ae/click/':
        raise Http404("A/B test click endpoint not found")
    
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])
    
    experiment_name = "button_label_kudos_vs_thanks"
    endpoint = "/218b7ae/"
    session_key_variant = f"abexp:{experiment_name}:variant"
    session_key_exposed = f"abexp:{experiment_name}:exposed:{endpoint}"
    
    # Ensure we have a session
    if not request.session.session_key:
        request.session.save()
    session_id = request.session.session_key
    
    # Variant from session only (NOT from POST body)
    variant = request.session.get(session_key_variant)
    if not variant:
        variant = random.choice(["kudos", "thanks"])
        request.session[session_key_variant] = variant
        request.session.modified = True
    
    # Backfill exposure if missing (check both session flag and DB)
    if not request.session.get(session_key_exposed):
        # Check DB to ensure we don't create duplicate
        existing_exposure = ABTestEvent.objects.filter(
            experiment_name=experiment_name,
            event_type=ABTestEvent.EVENT_TYPE_EXPOSURE,
            endpoint=endpoint,
            session_id=session_id,
        ).exists()
        
        if not existing_exposure:
            ABTestEvent.objects.get_or_create(
                experiment_name=experiment_name,
                event_type=ABTestEvent.EVENT_TYPE_EXPOSURE,
                endpoint=endpoint,
                session_id=session_id,
                defaults={"variant": variant},
            )
        request.session[session_key_exposed] = True
        request.session.modified = True
    
    # Log Conversion (every click)
    ABTestEvent.objects.create(
        experiment_name=experiment_name,
        event_type=ABTestEvent.EVENT_TYPE_CONVERSION,
        endpoint=endpoint,
        session_id=session_id,
        variant=variant,
    )
    
    response = JsonResponse({"status": "ok", "variant": variant})
    
    # Extra hardening: ensure no caching (some proxies/CDNs ignore decorators)
    response["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response["Pragma"] = "no-cache"
    response["Expires"] = "0"
    response["Vary"] = "Cookie"
    
    return response



