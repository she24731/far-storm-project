"""
Management command to create user groups.

Creates Reader, Contributor, and Admin groups.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from config.settings import READER_GROUP, CONTRIBUTOR_GROUP, ADMIN_GROUP


class Command(BaseCommand):
    help = 'Create user groups (Reader, Contributor, Admin)'

    def handle(self, *args, **options):
        groups_to_create = [
            (READER_GROUP, 'Can view approved posts'),
            (CONTRIBUTOR_GROUP, 'Can submit and edit posts'),
            (ADMIN_GROUP, 'Can approve/reject posts and manage content'),
        ]
        
        for group_name, description in groups_to_create:
            group, created = Group.objects.get_or_create(name=group_name)
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Created group: {group_name}'))
            else:
                self.stdout.write(f'  Group already exists: {group_name}')
        
        self.stdout.write(self.style.SUCCESS('\n✓ User groups setup complete!'))

