"""
Models for Yale Newcomer Survival Guide.

Defines Category, Post, Bookmark, and ExternalLink models.
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse


class Category(models.Model):
    """Category model for organizing posts."""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']
        indexes = [models.Index(fields=['slug'])]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('core:category_list', kwargs={'slug': self.slug})


class Post(models.Model):
    """Post model with status workflow: draft → pending → approved/rejected"""
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    content = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='posts')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['category_id']),
            models.Index(fields=['updated_at']),
        ]

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"

    def save(self, *args, **kwargs):
        """Auto-set published_at when status changes to approved."""
        if self.status == 'approved' and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('core:post_detail', kwargs={'slug': self.slug})


class Bookmark(models.Model):
    """Bookmark model for users to save posts."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookmarks')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='bookmarks')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'post']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} bookmarked {self.post.title}"


class ExternalLink(models.Model):
    """ExternalLink model for curated external resources."""
    title = models.CharField(max_length=200)
    url = models.URLField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='external_links', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title

