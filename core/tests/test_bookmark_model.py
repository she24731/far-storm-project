"""
Unit tests for Bookmark model.
"""
from django.test import TestCase
from django.contrib.auth.models import User
from core.models import Bookmark, Post, Category


class BookmarkModelTest(TestCase):
    """Test cases for Bookmark model."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create(
            name='Housing',
            slug='housing'
        )
        self.post = Post.objects.create(
            title='Test Post',
            slug='test-post',
            content='Content',
            category=self.category,
            author=self.user,
            status='approved'
        )
    
    def test_bookmark_creation(self):
        """Test creating a bookmark."""
        bookmark = Bookmark.objects.create(
            user=self.user,
            post=self.post
        )
        
        self.assertEqual(bookmark.user, self.user)
        self.assertEqual(bookmark.post, self.post)
        self.assertIsNotNone(bookmark.created_at)
    
    def test_bookmark_str_representation(self):
        """Test bookmark string representation."""
        bookmark = Bookmark.objects.create(
            user=self.user,
            post=self.post
        )
        expected_str = f"{self.user.username} bookmarked {self.post.title}"
        self.assertEqual(str(bookmark), expected_str)
    
    def test_bookmark_unique_together(self):
        """Test that a user can only bookmark a post once."""
        Bookmark.objects.create(
            user=self.user,
            post=self.post
        )
        
        # Attempting to create another bookmark for the same user and post should raise an error
        with self.assertRaises(Exception):
            Bookmark.objects.create(
                user=self.user,
                post=self.post
            )
    
    def test_bookmark_different_users_same_post(self):
        """Test that different users can bookmark the same post."""
        user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123'
        )
        
        bookmark1 = Bookmark.objects.create(
            user=self.user,
            post=self.post
        )
        bookmark2 = Bookmark.objects.create(
            user=user2,
            post=self.post
        )
        
        self.assertEqual(Bookmark.objects.count(), 2)
        self.assertNotEqual(bookmark1, bookmark2)
    
    def test_bookmark_same_user_different_posts(self):
        """Test that a user can bookmark multiple different posts."""
        post2 = Post.objects.create(
            title='Test Post 2',
            slug='test-post-2',
            content='Content 2',
            category=self.category,
            author=self.user,
            status='approved'
        )
        
        bookmark1 = Bookmark.objects.create(
            user=self.user,
            post=self.post
        )
        bookmark2 = Bookmark.objects.create(
            user=self.user,
            post=post2
        )
        
        self.assertEqual(Bookmark.objects.count(), 2)
        self.assertNotEqual(bookmark1, bookmark2)
    
    def test_bookmark_ordering(self):
        """Test that bookmarks are ordered by created_at descending."""
        post2 = Post.objects.create(
            title='Test Post 2',
            slug='test-post-2',
            content='Content 2',
            category=self.category,
            author=self.user,
            status='approved'
        )
        
        bookmark1 = Bookmark.objects.create(
            user=self.user,
            post=self.post
        )
        
        import time
        time.sleep(0.1)
        
        bookmark2 = Bookmark.objects.create(
            user=self.user,
            post=post2
        )
        
        bookmarks = list(Bookmark.objects.all())
        # Most recently created should be first
        self.assertEqual(bookmarks[0], bookmark2)
        self.assertEqual(bookmarks[1], bookmark1)
    
    def test_bookmark_cascade_delete_on_user(self):
        """Test that bookmarks are deleted when user is deleted."""
        bookmark = Bookmark.objects.create(
            user=self.user,
            post=self.post
        )
        
        self.user.delete()
        
        # Bookmark should be deleted
        self.assertEqual(Bookmark.objects.count(), 0)
    
    def test_bookmark_cascade_delete_on_post(self):
        """Test that bookmarks are deleted when post is deleted."""
        bookmark = Bookmark.objects.create(
            user=self.user,
            post=self.post
        )
        
        self.post.delete()
        
        # Bookmark should be deleted
        self.assertEqual(Bookmark.objects.count(), 0)

