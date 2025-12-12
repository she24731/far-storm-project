"""
URL configuration for Yale Newcomer Survival Guide.

Root URL patterns.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('218b7ae/', views.abtest_view, name='abtest'),  # A/B test endpoint for team far-storm
    path('218b7ae/click/', views.abtest_click, name='abtest_click'),  # A/B test click logging endpoint
    path('', include('core.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

