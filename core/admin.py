"""
Django admin configuration for core app.
"""

from django.contrib import admin
from django.contrib.admin import site
from .models import Category, Post, Bookmark, ExternalLink

# Customize admin site
site.site_header = "Yale Newcomer Survival Guide Admin"
site.site_title = "Yale Guide Admin"
site.index_title = "Welcome to the Administration Panel"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name', 'description']


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'author', 'status', 'created_at', 'updated_at']
    list_filter = ['status', 'category', 'created_at']
    search_fields = ['title', 'content']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['created_at', 'updated_at', 'published_at']
    
    fieldsets = (
        ('Content', {
            'fields': ('title', 'slug', 'content', 'category', 'author')
        }),
        ('Status', {
            'fields': ('status', 'published_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ExternalLink)
class ExternalLinkAdmin(admin.ModelAdmin):
    list_display = ['title', 'url', 'category', 'created_at']
    list_filter = ['category', 'created_at']
    search_fields = ['title', 'url']


@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ['user', 'post', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'post__title']

