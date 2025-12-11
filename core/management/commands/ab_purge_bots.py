"""
Django management command to purge bot-generated AB test events.

Usage:
    python manage.py ab_purge_bots [--dry-run]
"""

from django.core.management.base import BaseCommand
from django.db.models import Count
from django.db.models.functions import Length, TruncMinute
from django.utils import timezone
from datetime import timedelta
from core.models import ABTestEvent


class Command(BaseCommand):
    help = 'Delete AB test events that appear to be from bots or uptime checkers'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        self.stdout.write(self.style.SUCCESS('\n=== A/B Test Bot Data Purge ==='))
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No data will be deleted\n'))
        else:
            self.stdout.write(self.style.WARNING('LIVE MODE - Data will be permanently deleted\n'))
        
        total_deleted = 0
        
        # 1. Delete events where session_id starts with "e5e6" (Render bot pattern)
        qs1 = ABTestEvent.objects.filter(session_id__startswith='e5e6')
        count1 = qs1.count()
        if count1 > 0:
            self.stdout.write(f'1. Events with session_id starting with "e5e6": {count1}')
            if not dry_run:
                deleted1 = qs1.delete()[0]
                total_deleted += deleted1
                self.stdout.write(self.style.SUCCESS(f'   ✓ Deleted {deleted1} events'))
            else:
                self.stdout.write(f'   [DRY RUN] Would delete {count1} events')
        else:
            self.stdout.write('1. Events with session_id starting with "e5e6": 0')
        
        # 2. Delete events where user_id is NULL AND session_id length < 10
        # Filter by checking session_id length using annotation
        qs2 = ABTestEvent.objects.filter(user__isnull=True).annotate(sid_len=Length('session_id')).filter(sid_len__lt=10)
        count2 = qs2.count()
        if count2 > 0:
            self.stdout.write(f'\n2. Events with NULL user_id and session_id length < 10: {count2}')
            if not dry_run:
                deleted2 = qs2.delete()[0]
                total_deleted += deleted2
                self.stdout.write(self.style.SUCCESS(f'   ✓ Deleted {deleted2} events'))
            else:
                self.stdout.write(f'   [DRY RUN] Would delete {count2} events')
        else:
            self.stdout.write('\n2. Events with NULL user_id and session_id length < 10: 0')
        
        # 3. Delete events with >50 events per minute (burst pattern indicates bot)
        # Check for events created in 1-minute windows with >50 events
        # Group by minute and find suspicious bursts
        now = timezone.now()
        one_day_ago = now - timedelta(days=1)
        
        # Get all events from the last day, grouped by minute
        events_by_minute = (
            ABTestEvent.objects
            .filter(created_at__gte=one_day_ago)
            .annotate(minute=TruncMinute('created_at'))
            .values('minute')
            .annotate(count=Count('id'))
            .filter(count__gt=50)
        )
        
        count3 = 0
        if events_by_minute.exists():
            # Get all events in those high-volume minutes
            suspicious_minutes = [e['minute'] for e in events_by_minute]
            qs3 = (
                ABTestEvent.objects
                .filter(created_at__gte=one_day_ago)
                .annotate(minute=TruncMinute('created_at'))
                .filter(minute__in=suspicious_minutes)
            )
            count3 = qs3.count()
        
        if count3 > 0:
            self.stdout.write(f'\n3. Events in high-volume minutes (>50 per minute): {count3}')
            if not dry_run:
                # We need to delete the original objects, not the annotated ones
                # So we get the IDs and delete those
                event_ids = list(qs3.values_list('id', flat=True))
                deleted3 = ABTestEvent.objects.filter(id__in=event_ids).delete()[0]
                total_deleted += deleted3
                self.stdout.write(self.style.SUCCESS(f'   ✓ Deleted {deleted3} events'))
            else:
                self.stdout.write(f'   [DRY RUN] Would delete {count3} events')
        else:
            self.stdout.write('\n3. Events in high-volume minutes (>50 per minute): 0')
        
        # Summary
        self.stdout.write('\n' + '=' * 50)
        if dry_run:
            total_would_delete = count1 + count2 + count3
            self.stdout.write(self.style.WARNING(f'DRY RUN: Would delete {total_would_delete} events'))
            self.stdout.write('\nRun without --dry-run to actually delete the data.')
        else:
            self.stdout.write(self.style.SUCCESS(f'Total deleted: {total_deleted} events'))
        self.stdout.write('=' * 50 + '\n')

