"""
URL configuration for core app.

Defines all URL patterns for the application.
"""

from django.urls import path
from . import views
from . import views_admin_tools

app_name = 'core'

urlpatterns = [
    # Health check (must be first for fast response)
    path('health/', views.health_check, name='health'),
    
    # Public pages
    path('', views.home, name='home'),
    path('c/<slug:slug>/', views.category_list, name='category_list'),
    path('p/<slug:slug>/', views.post_detail, name='post_detail'),
    
    # Contributor pages
    path('submit/', views.submit_post, name='submit_post'),
    path('create/', views.submit_post, name='create_post'),  # Alias for better UX
    path('submit/<int:post_id>/', views.submit_post, name='submit_post_edit'),
    path('my-posts/', views.contributor_post_list, name='contributor_post_list'),
    path('my-posts/delete/<int:post_id>/', views.contributor_delete_post, name='contributor_delete_post'),
    path('p/<slug:slug>/bookmark/', views.bookmark_post, name='bookmark_post'),
    path('bookmarks/', views.bookmarks_list, name='bookmarks_list'),
    
    # Admin dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/approve/<int:post_id>/', views.approve_post, name='approve_post'),
    path('dashboard/reject/<int:post_id>/', views.reject_post, name='reject_post'),
    
    # Admin tools (no shell on Render)
    path(
        'admin-tools/ab-purge-bots/dry-run/',
        views_admin_tools.ab_purge_bots_dry_run,
        name='ab_purge_bots_dry_run',
    ),
    path(
        'admin-tools/ab-purge-bots/run/',
        views_admin_tools.ab_purge_bots_run,
        name='ab_purge_bots_run',
    ),
    
    # Authentication
    path('signup/', views.signup, name='signup'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
]

