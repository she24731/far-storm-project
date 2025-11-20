"""
Unit tests for Category model.
"""
from django.test import TestCase
from core.models import Category


class CategoryModelTest(TestCase):
    """Test cases for Category model."""
    
    def test_category_creation(self):
        """Test creating a category."""
        category = Category.objects.create(
            name='Housing',
            slug='housing',
            description='Housing related posts'
        )
        
        self.assertEqual(category.name, 'Housing')
        self.assertEqual(category.slug, 'housing')
        self.assertEqual(category.description, 'Housing related posts')
        self.assertIsNotNone(category.created_at)
    
    def test_category_str_representation(self):
        """Test category string representation."""
        category = Category.objects.create(
            name='Housing',
            slug='housing'
        )
        self.assertEqual(str(category), 'Housing')
    
    def test_category_get_absolute_url(self):
        """Test category get_absolute_url method."""
        category = Category.objects.create(
            name='Housing',
            slug='housing'
        )
        expected_url = f'/c/{category.slug}/'
        self.assertEqual(category.get_absolute_url(), expected_url)
    
    def test_category_unique_name(self):
        """Test that category names must be unique."""
        Category.objects.create(
            name='Housing',
            slug='housing'
        )
        
        # Attempting to create another category with the same name should raise an error
        with self.assertRaises(Exception):
            Category.objects.create(
                name='Housing',
                slug='housing-2'
            )
    
    def test_category_unique_slug(self):
        """Test that category slugs must be unique."""
        Category.objects.create(
            name='Housing',
            slug='housing'
        )
        
        # Attempting to create another category with the same slug should raise an error
        with self.assertRaises(Exception):
            Category.objects.create(
                name='Housing 2',
                slug='housing'
            )
    
    def test_category_ordering(self):
        """Test that categories are ordered by name."""
        Category.objects.create(name='Zebra', slug='zebra')
        Category.objects.create(name='Apple', slug='apple')
        Category.objects.create(name='Banana', slug='banana')
        
        categories = list(Category.objects.all())
        self.assertEqual(categories[0].name, 'Apple')
        self.assertEqual(categories[1].name, 'Banana')
        self.assertEqual(categories[2].name, 'Zebra')
    
    def test_category_blank_description(self):
        """Test that category description can be blank."""
        category = Category.objects.create(
            name='Housing',
            slug='housing',
            description=''
        )
        self.assertEqual(category.description, '')
    
    def test_category_verbose_name_plural(self):
        """Test category verbose name plural."""
        self.assertEqual(Category._meta.verbose_name_plural, 'Categories')

