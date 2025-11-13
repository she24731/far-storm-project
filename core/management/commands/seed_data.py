"""
Management command to seed initial data.

Creates categories, sample users, and sample posts.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from core.models import Category, Post
from config.settings import READER_GROUP, CONTRIBUTOR_GROUP, ADMIN_GROUP


class Command(BaseCommand):
    help = 'Seed initial data: groups, categories, users, and posts'

    def handle(self, *args, **options):
        self.stdout.write('Seeding initial data...\n')

        # Create groups
        self.stdout.write('Creating user groups...')
        for group_name in [READER_GROUP, CONTRIBUTOR_GROUP, ADMIN_GROUP]:
            group, created = Group.objects.get_or_create(name=group_name)
            if created:
                self.stdout.write(self.style.SUCCESS(f'  ✓ Created group: {group_name}'))

        # Create categories
        self.stdout.write('\nCreating categories...')
        categories_data = [
            {'name': 'Housing', 'slug': 'housing', 'description': 'Find safe and affordable housing options'},
            {'name': 'Food', 'slug': 'food', 'description': 'Best restaurants and meal options'},
            {'name': 'Transport', 'slug': 'transport', 'description': 'Getting around New Haven'},
            {'name': 'Academics', 'slug': 'academics', 'description': 'Class registration and study tips'},
            {'name': 'Groceries', 'slug': 'groceries', 'description': 'Where to shop for groceries'},
            {'name': 'Entertainment', 'slug': 'entertainment', 'description': 'Things to do in New Haven'},
            {'name': 'Athletics', 'slug': 'athletics', 'description': 'Gyms and fitness options'},
        ]

        created_categories = {}
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                slug=cat_data['slug'],
                defaults=cat_data
            )
            created_categories[cat_data['slug']] = category
            if created:
                self.stdout.write(self.style.SUCCESS(f'  ✓ Created category: {category.name}'))

        # Create admin user
        self.stdout.write('\nCreating admin user...')
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@example.com',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            admin_user.groups.add(Group.objects.get(name=ADMIN_GROUP))
            self.stdout.write(self.style.SUCCESS('  ✓ Created admin user (username: admin, password: admin123)'))
        else:
            self.stdout.write('  Admin user already exists')

        # Create contributor user
        contributor_user, created = User.objects.get_or_create(
            username='contributor',
            defaults={'email': 'contributor@example.com'}
        )
        if created:
            contributor_user.set_password('contributor123')
            contributor_user.save()
            contributor_user.groups.add(Group.objects.get(name=CONTRIBUTOR_GROUP))
            self.stdout.write(self.style.SUCCESS('  ✓ Created contributor user (username: contributor, password: contributor123)'))

        # Create sample posts
        self.stdout.write('\nCreating sample posts...')
        housing_category = created_categories.get('housing')
        if housing_category:
            # Approved post
            approved_post, created = Post.objects.get_or_create(
                slug='finding-off-campus-housing',
                defaults={
                    'title': 'Finding Off-Campus Housing in New Haven',
                    'content': '''# Finding Off-Campus Housing in New Haven

Finding the right housing can be challenging when you're new to New Haven. Here are some tips:

## Popular Neighborhoods

- **East Rock**: Close to campus, family-friendly, but can be expensive
- **Wooster Square**: Historic area, good restaurants nearby
- **Downtown**: Convenient but can be noisy
- **Westville**: More affordable, quieter, but further from campus

## Resources

- Check Yale's Off-Campus Housing website
- Join Facebook groups for Yale students
- Consider roommates to split costs

## Tips

- Start looking early (2-3 months before move-in)
- Visit in person if possible
- Check for heating/cooling systems
- Ask about utilities and parking

Good luck with your search!''',
                    'category': housing_category,
                    'author': admin_user,
                    'status': 'approved',
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'  ✓ Created approved post: {approved_post.title}'))

            # Pending post
            pending_post, created = Post.objects.get_or_create(
                slug='best-grocery-stores-new-haven',
                defaults={
                    'title': 'Best Grocery Stores in New Haven',
                    'content': 'This is a sample pending post waiting for admin approval.',
                    'category': created_categories.get('groceries', housing_category),
                    'author': contributor_user,
                    'status': 'pending',
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'  ✓ Created pending post: {pending_post.title}'))

        self.stdout.write(self.style.SUCCESS('\n✓ Seeding complete!'))

