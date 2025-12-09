"""
Django admin configuration for core app.
"""

from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from .models import Category, Post, Bookmark, ExternalLink, ABTestEvent

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

@admin.register(ABTestEvent)
class ABTestEventAdmin(admin.ModelAdmin):
    list_display = ("experiment_name", "variant", "event_type", "endpoint", "session_id", "created_at", "is_forced")
    list_filter = ("experiment_name", "variant", "event_type", "endpoint", "is_forced")
    search_fields = ("session_id", "ip_address", "user_agent")
    readonly_fields = ("created_at",)  # created_at is auto-set, make it readonly
    list_per_page = 100  # Show more events per page
    date_hierarchy = "created_at"  # Add date navigation

    def get_urls(self):
        """Add custom URL for A/B test summary dashboard."""
        urls = super().get_urls()
        custom_urls = [
            path(
                'abtest-summary/',
                self.admin_site.admin_view(self.abtest_summary_view),
                name='core_abtestevent_abtest_summary',
            ),
        ]
        return custom_urls + urls

    def changelist_view(self, request, extra_context=None):
        """Add link to A/B test summary in changelist."""
        extra_context = extra_context or {}
        extra_context['summary_url'] = 'admin:core_abtestevent_abtest_summary'
        return super().changelist_view(request, extra_context)

    def abtest_summary_view(self, request):
        """
        A/B test summary dashboard view.
        Groups ABTestEvent data by experiment and variant, showing impressions,
        conversions, conversion rates, and uplift.
        """
        # Query all events grouped by experiment_name and variant
        experiments_data = {}
        
        # Get all unique experiments
        experiments = ABTestEvent.objects.values_list('experiment_name', flat=True).distinct()
        
        for exp_name in experiments:
            variants_data = {}
            
            # Get all variants for this experiment
            variants = ABTestEvent.objects.filter(
                experiment_name=exp_name
            ).values_list('variant', flat=True).distinct()
            
            for variant in variants:
                # Count impressions (exposure events)
                impressions = ABTestEvent.objects.filter(
                    experiment_name=exp_name,
                    variant=variant,
                    event_type=ABTestEvent.EVENT_TYPE_EXPOSURE
                ).count()
                
                # Count conversions (conversion events)
                conversions = ABTestEvent.objects.filter(
                    experiment_name=exp_name,
                    variant=variant,
                    event_type=ABTestEvent.EVENT_TYPE_CONVERSION
                ).count()
                
                # Calculate conversion rate as percentage (0-100)
                conversion_rate = ((conversions / impressions) * 100) if impressions > 0 else 0.0
                
                variants_data[variant] = {
                    'variant': variant,
                    'impressions': impressions,
                    'conversions': conversions,
                    'conversion_rate': conversion_rate,
                }
            
            # Calculate uplift for each variant vs the best variant (baseline)
            if variants_data:
                # Find the variant with the highest conversion rate (baseline)
                baseline_variant = max(
                    variants_data.keys(),
                    key=lambda v: variants_data[v]['conversion_rate']
                )
                baseline_rate = variants_data[baseline_variant]['conversion_rate']
                
                # Calculate uplift for each variant
                for variant_key, variant_info in variants_data.items():
                    if variant_key == baseline_variant:
                        variant_info['uplift_vs_baseline'] = None  # Baseline has no uplift
                    else:
                        if baseline_rate > 0:
                            # Uplift as percentage (multiply by 100 to show as percentage points)
                            uplift = ((variant_info['conversion_rate'] - baseline_rate) / baseline_rate) * 100
                            variant_info['uplift_vs_baseline'] = uplift
                        else:
                            variant_info['uplift_vs_baseline'] = None
            
            experiments_data[exp_name] = {
                'name': exp_name,
                'variants': list(variants_data.values()),
            }
        
        context = {
            'title': 'A/B Test Summary',
            'experiments': list(experiments_data.values()),
            'has_perm': request.user.has_perm('core.view_abtestevent'),
        }
        
        return render(request, 'admin/abtest_summary.html', context)

