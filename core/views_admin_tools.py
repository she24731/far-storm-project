"""
Admin-only HTTP endpoints for management tools.

These endpoints allow running management commands via HTTP when shell access
is not available (e.g., on Render production environment).
"""
from django.http import JsonResponse
from django.core.management import call_command
from django.views.decorators.http import require_GET
from django.contrib.admin.views.decorators import staff_member_required
from io import StringIO


@staff_member_required
@require_GET
def ab_purge_bots_dry_run(request):
    """
    Admin-only endpoint that runs ab_purge_bots in DRY-RUN mode.
    
    Use this first to see how many events *would* be deleted.
    
    URL: /admin-tools/ab-purge-bots/dry-run/
    """
    # Capture command output to include in response
    out = StringIO()
    call_command("ab_purge_bots", dry_run=True, stdout=out)
    output = out.getvalue()
    
    return JsonResponse(
        {
            "status": "ok",
            "mode": "dry_run",
            "detail": "ab_purge_bots dry run completed on this environment.",
            "output": output,
        }
    )


@staff_member_required
@require_GET
def ab_purge_bots_run(request):
    """
    Admin-only endpoint that runs ab_purge_bots in REAL delete mode.
    
    Only use this after verifying the dry-run looks correct.
    
    URL: /admin-tools/ab-purge-bots/run/
    """
    # Capture command output to include in response
    out = StringIO()
    call_command("ab_purge_bots", stdout=out)
    output = out.getvalue()
    
    return JsonResponse(
        {
            "status": "ok",
            "mode": "run",
            "detail": "ab_purge_bots executed and bot events were purged on this environment.",
            "output": output,
        }
    )

