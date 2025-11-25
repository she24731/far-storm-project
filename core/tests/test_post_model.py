"""
Unit tests for Post model.
"""
from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from core.models import Post, Category


class PostModelTest(TestCase):
    """Test cases for Post model."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create(
            name='Housing',
            slug='housing',
            description='Housing related posts'
        )
    
    def test_post_creation(self):
        """Test creating a post."""
        post = Post.objects.create(
            title='Test Post',
            slug='test-post',
            content='This is a test post content.',
            category=self.category,
            author=self.user,
            status='draft'
        )
        
        self.assertEqual(post.title, 'Test Post')
        self.assertEqual(post.slug, 'test-post')
        self.assertEqual(post.content, 'This is a test post content.')
        self.assertEqual(post.category, self.category)
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.status, 'draft')
        self.assertIsNone(post.published_at)
    
    def test_post_str_representation(self):
        """Test post string representation."""
        post = Post.objects.create(
            title='Test Post',
            slug='test-post',
            content='Content',
            category=self.category,
            author=self.user,
            status='pending'
        )
        self.assertEqual(str(post), 'Test Post (Pending Review)')
    
    def test_post_get_absolute_url(self):
        """Test post get_absolute_url method."""
        post = Post.objects.create(
            title='Test Post',
            slug='test-post',
            content='Content',
            category=self.category,
            author=self.user
        )
        expected_url = f'/p/{post.slug}/'
        self.assertEqual(post.get_absolute_url(), expected_url)
    
    def test_post_auto_set_published_at_on_approval(self):
        """Test that published_at is automatically set when status changes to approved."""
        post = Post.objects.create(
            title='Test Post',
            slug='test-post',
            content='Content',
            category=self.category,
            author=self.user,
            status='draft'
        )
        
        # Initially published_at should be None
        self.assertIsNone(post.published_at)
        
        # Change status to approved
        post.status = 'approved'
        post.save()
        
        # published_at should now be set
        self.assertIsNotNone(post.published_at)
        self.assertAlmostEqual(
            post.published_at,
            timezone.now(),
            delta=timezone.timedelta(seconds=5)
        )
    
    def test_post_published_at_not_overwritten(self):
        """Test that published_at is not overwritten if already set."""
        past_date = timezone.now() - timezone.timedelta(days=1)
        post = Post.objects.create(
            title='Test Post',
            slug='test-post',
            content='Content',
            category=self.category,
            author=self.user,
            status='approved',
            published_at=past_date
        )
        
        # Change status and save again
        post.status = 'rejected'
        post.save()
        post.status = 'approved'
        post.save()
        
        # published_at should remain the original date
        self.assertEqual(post.published_at, past_date)
    
    def test_post_status_choices(self):
        """Test post status choices."""
        statuses = [choice[0] for choice in Post.STATUS_CHOICES]
        self.assertIn('draft', statuses)
        self.assertIn('pending', statuses)
        self.assertIn('approved', statuses)
        self.assertIn('rejected', statuses)
    
    def test_post_default_status(self):
        """Test that post defaults to draft status."""
        post = Post.objects.create(
            title='Test Post',
            slug='test-post',
            content='Content',
            category=self.category,
            author=self.user
        )
        self.assertEqual(post.status, 'draft')
    
    def test_post_ordering(self):
        """Test that posts are ordered by updated_at descending."""
        post1 = Post.objects.create(
            title='Post 1',
            slug='post-1',
            content='Content 1',
            category=self.category,
            author=self.user
        )
        post2 = Post.objects.create(
            title='Post 2',
            slug='post-2',
            content='Content 2',
            category=self.category,
            author=self.user
        )
        
        posts = list(Post.objects.all())
        # Most recently updated should be first
        self.assertEqual(posts[0], post2)
        self.assertEqual(posts[1], post1)
    
    def test_auto_slug_generation_from_title(self):
        """Test that slug is automatically generated from title when not provided."""
        post = Post.objects.create(
            title='Chun-Hung needs French teacher !',
            slug='',  # Empty slug
            content='Content',
            category=self.category,
            author=self.user
        )
        
        # Slug should be auto-generated from title
        self.assertEqual(post.slug, 'chun-hung-needs-french-teacher')
    
    def test_auto_slug_generation_unique(self):
        """Test that auto-generated slugs are unique when titles are the same."""
        # Create first post with same title pattern
        post1 = Post.objects.create(
            title='Chun-Hung needs French teacher !',
            slug='',
            content='Content 1',
            category=self.category,
            author=self.user
        )
        
        # Create second post with same title
        post2 = Post.objects.create(
            title='Chun-Hung needs French teacher !',
            slug='',
            content='Content 2',
            category=self.category,
            author=self.user
        )
        
        # Slugs should be unique
        self.assertEqual(post1.slug, 'chun-hung-needs-french-teacher')
        self.assertEqual(post2.slug, 'chun-hung-needs-french-teacher-2')
        self.assertNotEqual(post1.slug, post2.slug)
    
    def test_auto_slug_generation_unique_with_existing_slug(self):
        """Test that auto-generated slugs handle existing slugs correctly."""
        # Create post with explicit slug
        post1 = Post.objects.create(
            title='Test Post',
            slug='test-post',
            content='Content 1',
            category=self.category,
            author=self.user
        )
        
        # Create another post that would generate same slug
        post2 = Post.objects.create(
            title='Test Post',
            slug='',  # Will auto-generate
            content='Content 2',
            category=self.category,
            author=self.user
        )
        
        # Should generate unique slug
        self.assertEqual(post1.slug, 'test-post')
        self.assertEqual(post2.slug, 'test-post-2')
    
    def test_slug_not_overwritten_if_provided(self):
        """Test that if slug is provided, it is not overwritten."""
        post = Post.objects.create(
            title='Test Post Title',
            slug='custom-slug',
            content='Content',
            category=self.category,
            author=self.user
        )
        
        # Slug should remain as provided
        self.assertEqual(post.slug, 'custom-slug')
        
        # Update title but slug should remain
        post.title = 'New Title'
        post.save()
        self.assertEqual(post.slug, 'custom-slug')

