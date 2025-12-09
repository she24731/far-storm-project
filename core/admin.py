"""
Django admin configuration for core app.
"""

from django.contrib import admin
from django.urls import path
from django.template.response import TemplateResponse
from django.db.models import Count
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
        
        Uses a single aggregated query to efficiently fetch all counts.
        Groups by experiment_name, variant, and event_type to avoid N+1 queries.
        Uses ONLY canonical event types: EVENT_TYPE_EXPOSURE and EVENT_TYPE_CONVERSION.
        """
        # Single aggregated query - no loops with filter().count()
        qs = (
            ABTestEvent.objects
            .values("experiment_name", "variant", "event_type")
            .annotate(count=Count("id"))
        )
        
        # Build in-memory structure from aggregated results
        experiments = {}
        
        for row in qs:
            exp = row["experiment_name"]
            variant = row["variant"]
            etype = row["event_type"]
            count = row["count"]
            
            # Initialize nested dicts if needed
            if exp not in experiments:
                experiments[exp] = {}
            if variant not in experiments[exp]:
                experiments[exp][variant] = {
                    "impressions": 0,
                    "conversions": 0,
                }
            
            # Populate counts based on event type
            if etype == ABTestEvent.EVENT_TYPE_EXPOSURE:
                experiments[exp][variant]["impressions"] = count
            elif etype == ABTestEvent.EVENT_TYPE_CONVERSION:
                experiments[exp][variant]["conversions"] = count
        
        # Compute conversion rates and build summary data
        summary_data = []
        
        for exp, variants in experiments.items():
            if not variants:
                continue
            
            variant_items = list(variants.items())
            
            # Compute conversion rates
            for variant_name, stats in variant_items:
                impressions = stats.get("impressions", 0) or 0
                conversions = stats.get("conversions", 0) or 0
                
                if impressions > 0:
                    rate = conversions / impressions
                else:
                    rate = 0.0
                
                stats["conversion_rate"] = rate
            
            # Find baseline (variant with highest conversion_rate)
            max_rate = max(v["conversion_rate"] for v in variants.values())
            
            if max_rate > 0:
                # Actual baseline(s) - variants with highest rate
                baselines = [
                    name for name, s in variant_items
                    if s["conversion_rate"] == max_rate
                ]
            else:
                # All rates are 0 - pick first variant as baseline for display
                baselines = [variant_items[0][0]]
            
            baseline_rate = max_rate  # Could be 0.0
            
            # Build summary rows with uplift calculations
            for variant_name, stats in variant_items:
                impressions = stats.get("impressions", 0) or 0
                conversions = stats.get("conversions", 0) or 0
                rate = stats.get("conversion_rate", 0.0) or 0.0
                is_baseline = variant_name in baselines
                
                # Compute uplift display
                if is_baseline:
                    uplift_display = "Baseline"
                else:
                    if baseline_rate > 0:
                        uplift_pct = (rate - baseline_rate) / baseline_rate * 100.0
                        uplift_display = f"{uplift_pct:+.2f}%"
                    else:
                        uplift_display = "N/A"
                
                summary_data.append({
                    "experiment_name": exp,
                    "variant": variant_name,
                    "impressions": impressions,
                    "conversions": conversions,
                    "conversion_rate": rate,
                    "conversion_rate_display": f"{rate * 100:.2f}%",
                    "uplift_display": uplift_display,
                    "is_baseline": is_baseline,
                })
        
        # Build context
        context = dict(
            self.admin_site.each_context(request),
            title="A/B Test Summary",
            summary_data=summary_data,
        )
        
        return TemplateResponse(request, "admin/abtest_summary.html", context)

