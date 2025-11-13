"""
Django admin configuration for the guide app.

This file registers models with the Django admin interface
for easy content management.
"""

from django.contrib import admin
from django.contrib.admin import site
from .models import Category, Post, ExternalLink, Bookmark

# Customize admin site headers
site.site_header = "Yale Newcomer Survival Guide Admin"
site.site_title = "Yale Guide Admin"
site.index_title = "Welcome to the Administration Panel"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin interface for Category model."""
    list_display = ['name', 'slug', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name', 'description']


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """Admin interface for Post model."""
    list_display = ['title', 'category', 'author', 'status', 'created_at', 'updated_at']
    list_filter = ['status', 'category', 'created_at']
    search_fields = ['title', 'content', 'summary']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['created_at', 'updated_at', 'published_at']
    
    fieldsets = (
        ('Content', {
            'fields': ('title', 'slug', 'content', 'summary', 'category', 'image')
        }),
        ('Status & Author', {
            'fields': ('status', 'author', 'published_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ExternalLink)
class ExternalLinkAdmin(admin.ModelAdmin):
    """Admin interface for ExternalLink model."""
    list_display = ['title', 'url', 'category', 'created_at']
    list_filter = ['category', 'created_at']
    search_fields = ['title', 'url', 'description']


@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    """Admin interface for Bookmark model."""
    list_display = ['user', 'post', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'post__title']

