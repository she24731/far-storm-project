"""
Models for the Yale Newcomer Survival Guide application.

This module defines the database models for categories, posts, bookmarks,
and external links.
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse


class Category(models.Model):
    """
    Category model for organizing posts.
    
    Categories include: Housing, Food, Transport, Academics, etc.
    """
    name = models.CharField(max_length=100, unique=True, help_text="Category name (e.g., Housing, Food)")
    slug = models.SlugField(max_length=100, unique=True, help_text="URL-friendly version of name")
    description = models.TextField(blank=True, help_text="Brief description of the category")
    icon = models.CharField(
        max_length=50, 
        blank=True, 
        help_text="Bootstrap icon class name (e.g., 'house-door', 'cup-hot')"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']
        indexes = [
            models.Index(fields=['slug']),
        ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('guide:category_detail', kwargs={'slug': self.slug})


class Post(models.Model):
    """
    Post model representing a tip or guide entry.
    
    Posts go through a workflow: draft → pending → approved/rejected
    """
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    # Core content fields
    title = models.CharField(max_length=200, help_text="Post title")
    slug = models.SlugField(max_length=200, unique=True, help_text="URL-friendly version of title")
    content = models.TextField(help_text="Post content (Markdown supported)")
    summary = models.TextField(
        max_length=300, 
        blank=True, 
        help_text="Brief summary for listings (optional)"
    )
    
    # Relationships
    category = models.ForeignKey(
        Category, 
        on_delete=models.CASCADE, 
        related_name='posts',
        help_text="Category this post belongs to"
    )
    author = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='posts',
        help_text="User who created this post"
    )
    
    # Status workflow
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='draft',
        help_text="Current status in the approval workflow"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(
        null=True, 
        blank=True, 
        help_text="Set automatically when status changes to approved"
    )
    
    # Optional image
    image = models.ImageField(
        upload_to='posts/', 
        blank=True, 
        null=True,
        help_text="Optional image for the post"
    )

    class Meta:
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['category']),
            models.Index(fields=['updated_at']),
            models.Index(fields=['slug']),
        ]

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"

    def save(self, *args, **kwargs):
        """Override save to auto-set published_at when approved."""
        if self.status == 'approved' and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('guide:post_detail', kwargs={'slug': self.slug})


class Bookmark(models.Model):
    """
    Bookmark model for users to save posts.
    
    Many-to-many relationship between Users and Posts.
    """
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='bookmarks',
        help_text="User who bookmarked this post"
    )
    post = models.ForeignKey(
        Post, 
        on_delete=models.CASCADE, 
        related_name='bookmarks',
        help_text="Post that was bookmarked"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'post']  # Prevent duplicate bookmarks
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'post']),
        ]

    def __str__(self):
        return f"{self.user.username} bookmarked {self.post.title}"


class ExternalLink(models.Model):
    """
    ExternalLink model for curated external resources.
    
    These are vetted links that can be displayed alongside posts.
    """
    title = models.CharField(max_length=200, help_text="Link title")
    url = models.URLField(help_text="External URL")
    description = models.TextField(blank=True, help_text="Description of the link")
    category = models.ForeignKey(
        Category, 
        on_delete=models.CASCADE, 
        related_name='external_links',
        null=True,
        blank=True,
        help_text="Optional category association"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['title']
        indexes = [
            models.Index(fields=['category']),
        ]

    def __str__(self):
        return self.title

