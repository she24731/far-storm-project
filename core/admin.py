"""
Django admin configuration for core app.
"""

from django.contrib import admin
from .models import Category, Post, Bookmark, ExternalLink

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")     # keep simple; no created_at assumed
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    # ONLY fields that we know exist on Post:
    list_display = ("title", "category", "status", "author", "updated_at")
    list_filter  = ("status", "category", "updated_at")
    search_fields = ("title", "content")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ()  # leave empty to avoid referencing non-existent attributes

    actions = ["approve_posts", "reject_posts"]

    def approve_posts(self, request, queryset):
        queryset.update(status="approved")
    approve_posts.short_description = "Approve selected posts"

    def reject_posts(self, request, queryset):
        queryset.update(status="rejected")
    reject_posts.short_description = "Reject selected posts"

@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ("user", "post")
    search_fields = ("user__username", "post__title")

@admin.register(ExternalLink)
class ExternalLinkAdmin(admin.ModelAdmin):
    list_display = ("title", "url", "category")
    search_fields = ("title", "url")

