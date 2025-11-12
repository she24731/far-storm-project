"""
URL configuration for the guide application.

This file defines all URL patterns for the guide app, including
home, category, post, search, and authentication routes.
"""

from django.urls import path
from . import views

app_name = 'guide'

urlpatterns = [
    # Home page
    path('', views.home, name='home'),
    
    # Category views
    path('category/<slug:slug>/', views.category_detail, name='category_detail'),
    
    # Post views
    path('post/<slug:slug>/', views.post_detail, name='post_detail'),
    
    # Search
    path('search/', views.search, name='search'),
    
    # Bookmarks (requires login)
    path('bookmark/<slug:post_slug>/', views.toggle_bookmark, name='toggle_bookmark'),
    
    # Authentication
    path('signup/', views.signup, name='signup'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
]

