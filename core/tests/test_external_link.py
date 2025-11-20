"""
Unit tests for ExternalLink model.
"""
from django.test import TestCase
from core.models import ExternalLink, Category


class ExternalLinkModelTest(TestCase):
    """Test cases for ExternalLink model."""
    
    def setUp(self):
        """Set up test data."""
        self.category = Category.objects.create(
            name='Housing',
            slug='housing'
        )
    
    def test_external_link_creation(self):
        """Test creating an external link."""
        link = ExternalLink.objects.create(
            title='Yale Housing',
            url='https://housing.yale.edu',
            category=self.category
        )
        
        self.assertEqual(link.title, 'Yale Housing')
        self.assertEqual(link.url, 'https://housing.yale.edu')
        self.assertEqual(link.category, self.category)
        self.assertIsNotNone(link.created_at)
        self.assertIsNotNone(link.updated_at)
    
    def test_external_link_str_representation(self):
        """Test external link string representation."""
        link = ExternalLink.objects.create(
            title='Yale Housing',
            url='https://housing.yale.edu',
            category=self.category
        )
        self.assertEqual(str(link), 'Yale Housing')
    
    def test_external_link_without_category(self):
        """Test creating an external link without a category."""
        link = ExternalLink.objects.create(
            title='Yale Website',
            url='https://yale.edu'
        )
        
        self.assertEqual(link.title, 'Yale Website')
        self.assertEqual(link.url, 'https://yale.edu')
        self.assertIsNone(link.category)
    
    def test_external_link_ordering(self):
        """Test that external links are ordered by title."""
        ExternalLink.objects.create(title='Zebra Link', url='https://zebra.com')
        ExternalLink.objects.create(title='Apple Link', url='https://apple.com')
        ExternalLink.objects.create(title='Banana Link', url='https://banana.com')
        
        links = list(ExternalLink.objects.all())
        self.assertEqual(links[0].title, 'Apple Link')
        self.assertEqual(links[1].title, 'Banana Link')
        self.assertEqual(links[2].title, 'Zebra Link')
    
    def test_external_link_auto_timestamps(self):
        """Test that created_at and updated_at are automatically set."""
        link = ExternalLink.objects.create(
            title='Test Link',
            url='https://test.com'
        )
        
        self.assertIsNotNone(link.created_at)
        self.assertIsNotNone(link.updated_at)
    
    def test_external_link_updated_at_changes(self):
        """Test that updated_at changes when link is modified."""
        link = ExternalLink.objects.create(
            title='Test Link',
            url='https://test.com'
        )
        
        original_updated_at = link.updated_at
        
        # Wait a moment and update
        import time
        time.sleep(0.1)
        link.title = 'Updated Link'
        link.save()
        
        # updated_at should have changed
        self.assertGreater(link.updated_at, original_updated_at)

