"""
Management command to seed initial data for the application.

This command creates:
- User groups (Reader, Contributor, Admin)
- Sample categories (Housing, Food, Transport, Academics, etc.)
- Sample users for each role
- Sample posts
- Sample external links

Run with: python manage.py seed_data
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from guide.models import Category, Post, ExternalLink
from yale_newcomer_survival_guide.settings import READER_GROUP, CONTRIBUTOR_GROUP, ADMIN_GROUP


class Command(BaseCommand):
    help = 'Seed initial data: groups, categories, users, posts, and external links'

    def handle(self, *args, **options):
        self.stdout.write('Seeding initial data...\n')

        # Create groups
        self.stdout.write('Creating user groups...')
        for group_name in [READER_GROUP, CONTRIBUTOR_GROUP, ADMIN_GROUP]:
            group, created = Group.objects.get_or_create(name=group_name)
            if created:
                self.stdout.write(self.style.SUCCESS(f'  ✓ Created group: {group_name}'))
            else:
                self.stdout.write(f'  Group already exists: {group_name}')

        # Create categories
        self.stdout.write('\nCreating categories...')
        categories_data = [
            {
                'name': 'Housing',
                'slug': 'housing',
                'description': 'Find safe and affordable housing options in New Haven',
                'icon': 'house-door',
            },
            {
                'name': 'Food & Dining',
                'slug': 'food-dining',
                'description': 'Best restaurants, grocery stores, and meal options',
                'icon': 'cup-hot',
            },
            {
                'name': 'Transportation',
                'slug': 'transportation',
                'description': 'Getting around New Haven and beyond',
                'icon': 'bus-front',
            },
            {
                'name': 'Academics',
                'slug': 'academics',
                'description': 'Class registration, study tips, and academic resources',
                'icon': 'book',
            },
            {
                'name': 'Groceries',
                'slug': 'groceries',
                'description': 'Where to shop for groceries and essentials',
                'icon': 'cart',
            },
            {
                'name': 'Entertainment',
                'slug': 'entertainment',
                'description': 'Things to do in New Haven and nearby',
                'icon': 'music-note-beamed',
            },
            {
                'name': 'Athletics',
                'slug': 'athletics',
                'description': 'Gyms, sports facilities, and fitness options',
                'icon': 'trophy',
            },
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
            else:
                self.stdout.write(f'  Category already exists: {category.name}')

        # Create sample users
        self.stdout.write('\nCreating sample users...')
        
        # Reader user
        reader_user, created = User.objects.get_or_create(
            username='reader',
            defaults={
                'email': 'reader@example.com',
                'first_name': 'Sample',
                'last_name': 'Reader',
            }
        )
        if created:
            reader_user.set_password('reader123')
            reader_user.save()
            reader_user.groups.add(Group.objects.get(name=READER_GROUP))
            self.stdout.write(self.style.SUCCESS('  ✓ Created reader user (username: reader, password: reader123)'))
        else:
            self.stdout.write('  Reader user already exists')

        # Contributor user
        contributor_user, created = User.objects.get_or_create(
            username='contributor',
            defaults={
                'email': 'contributor@example.com',
                'first_name': 'Sample',
                'last_name': 'Contributor',
            }
        )
        if created:
            contributor_user.set_password('contributor123')
            contributor_user.save()
            contributor_user.groups.add(Group.objects.get(name=CONTRIBUTOR_GROUP))
            self.stdout.write(self.style.SUCCESS('  ✓ Created contributor user (username: contributor, password: contributor123)'))
        else:
            self.stdout.write('  Contributor user already exists')

        # Admin user
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@example.com',
                'first_name': 'Sample',
                'last_name': 'Admin',
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

        # Create sample posts
        self.stdout.write('\nCreating sample posts...')
        housing_category = created_categories.get('housing')
        if housing_category and not Post.objects.filter(category=housing_category).exists():
            sample_post = Post.objects.create(
                title='Finding Off-Campus Housing in New Haven',
                slug='finding-off-campus-housing',
                content='''# Finding Off-Campus Housing in New Haven

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
                category=housing_category,
                author=contributor_user if contributor_user else admin_user,
                status='approved',
                summary='A comprehensive guide to finding off-campus housing in New Haven, including popular neighborhoods and helpful tips.',
            )
            self.stdout.write(self.style.SUCCESS(f'  ✓ Created sample post: {sample_post.title}'))

        # Create sample external links
        self.stdout.write('\nCreating sample external links...')
        if housing_category:
            link, created = ExternalLink.objects.get_or_create(
                url='https://offcampushousing.yale.edu',
                defaults={
                    'title': 'Yale Off-Campus Housing',
                    'description': 'Official Yale off-campus housing resources',
                    'category': housing_category,
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'  ✓ Created external link: {link.title}'))

        self.stdout.write(self.style.SUCCESS('\n✓ Seeding complete!'))

