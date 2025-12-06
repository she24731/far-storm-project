"""
Models for Yale Newcomer Survival Guide.

Defines Category, Post, Bookmark, and ExternalLink models.
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.text import slugify
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

    def _generate_unique_slug(self):
        """Generate a unique slug based on the post title."""
        base_slug = slugify(self.title) or "post"
        slug = base_slug
        counter = 2
        
        # Avoid infinite loops: only look at other posts, not self
        Model = self.__class__
        
        while Model.objects.filter(slug=slug).exclude(pk=self.pk).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        
        return slug

    def save(self, *args, **kwargs):
        """Auto-generate slug if empty, and auto-set published_at when status changes to approved."""
        # Auto-generate slug if it's empty or blank
        if not self.slug:
            self.slug = self._generate_unique_slug()
        
        # Auto-set published_at when status changes to approved
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


class ABTestEvent(models.Model):
    """
    Model to store A/B test events server-side for traffic split analysis.
    
    Tracks variant exposures and conversions for proper A/B test evaluation.
    Matches the specification: ab_events table structure.
    """
    EVENT_TYPE_CHOICES = [
        ('exposure', 'Variant Shown'),
        ('conversion', 'Button Clicked'),  # Changed from 'click' to 'conversion' per spec
    ]
    
    # Using experiment_name instead of experiment for clarity, but serves same purpose
    experiment_name = models.CharField(max_length=100, db_index=True, help_text="Experiment identifier, e.g. 'button_label_kudos_vs_thanks'")
    variant = models.CharField(max_length=20, db_index=True, help_text="Variant identifier, e.g. 'kudos' or 'thanks'")
    event_type = models.CharField(max_length=20, choices=EVENT_TYPE_CHOICES, db_index=True)
    endpoint = models.CharField(max_length=200, default='/218b7ae/', help_text="Endpoint path, e.g. '/218b7ae/'")
    user_id = models.CharField(max_length=100, null=True, blank=True, db_index=True, help_text="User identifier if available (from Django User or session)")
    session_id = models.CharField(max_length=100, db_index=True, help_text="Cookie-based session identifier")
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    is_forced = models.BooleanField(default=False, help_text="True if variant was forced via ?force_variant parameter")
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['experiment_name', 'variant', 'event_type']),
            models.Index(fields=['experiment_name', 'created_at']),
            models.Index(fields=['endpoint', 'event_type']),
        ]
        verbose_name = "AB Test Event"
        verbose_name_plural = "AB Test Events"
    
    def __str__(self):
        return f"{self.experiment_name} - {self.variant} - {self.event_type} ({self.created_at})"

