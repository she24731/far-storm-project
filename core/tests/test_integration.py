"""
Integration tests for user flows and workflows.
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User, Group
from django.urls import reverse
from core.models import Post, Category, Bookmark
from config.settings import CONTRIBUTOR_GROUP


class SignupFlowTest(TestCase):
    """Test signup flow."""
    
    def setUp(self):
        """Set up test client."""
        self.client = Client()
        # Ensure Contributor group exists
        Group.objects.get_or_create(name=CONTRIBUTOR_GROUP)
    
    def test_signup_creates_user(self):
        """Test that signup creates a new user."""
        response = self.client.post(reverse('core:signup'), {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123'
        })
        
        self.assertEqual(response.status_code, 302)  # Redirect after signup
        self.assertTrue(User.objects.filter(username='newuser').exists())
    
    def test_signup_assigns_contributor_role(self):
        """Test that new users are assigned to Contributor group."""
        contributor_group = Group.objects.get_or_create(name=CONTRIBUTOR_GROUP)[0]
        
        response = self.client.post(reverse('core:signup'), {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123'
        })
        
        user = User.objects.get(username='newuser')
        self.assertTrue(user.groups.filter(name=CONTRIBUTOR_GROUP).exists())
    
    def test_signup_auto_login(self):
        """Test that user is automatically logged in after signup."""
        response = self.client.post(reverse('core:signup'), {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123'
        }, follow=True)
        
        # User should be authenticated
        self.assertTrue(response.context['user'].is_authenticated)
        self.assertEqual(response.context['user'].username, 'newuser')


class LoginFlowTest(TestCase):
    """Test login flow."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_login_with_valid_credentials(self):
        """Test login with valid credentials."""
        response = self.client.post(reverse('core:login'), {
            'username': 'testuser',
            'password': 'testpass123'
        }, follow=True)
        
        self.assertTrue(response.context['user'].is_authenticated)
        self.assertEqual(response.context['user'].username, 'testuser')
    
    def test_login_with_invalid_credentials(self):
        """Test login with invalid credentials."""
        response = self.client.post(reverse('core:login'), {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        
        self.assertFalse(response.context['user'].is_authenticated)
    
    def test_login_redirects_authenticated_user(self):
        """Test that authenticated users are redirected from login page."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('core:login'))
        
        # Should redirect (302) or show home page
        self.assertIn(response.status_code, [200, 302])


class ContributorPostCreationTest(TestCase):
    """Test contributor creating a post."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='contributor',
            email='contributor@example.com',
            password='testpass123'
        )
        self.contributor_group = Group.objects.get_or_create(name=CONTRIBUTOR_GROUP)[0]
        self.user.groups.add(self.contributor_group)
        
        self.category = Category.objects.create(
            name='Housing',
            slug='housing'
        )
        
        self.client.login(username='contributor', password='testpass123')
    
    def test_contributor_can_access_create_post_page(self):
        """Test that contributor can access create post page."""
        response = self.client.get(reverse('core:submit_post'))
        self.assertEqual(response.status_code, 200)
    
    def test_contributor_can_create_post(self):
        """Test that contributor can create a new post without providing slug."""
        response = self.client.post(reverse('core:submit_post'), {
            'title': 'New Post',
            'content': 'This is a new post.',
            'category': self.category.id,
            'status': 'pending'
        })
        
        self.assertEqual(response.status_code, 302)  # Redirect after creation
        self.assertTrue(Post.objects.filter(title='New Post').exists())
        
        post = Post.objects.get(title='New Post')
        self.assertEqual(post.title, 'New Post')
        # Slug should be auto-generated
        self.assertEqual(post.slug, 'new-post')
        self.assertIsNotNone(post.slug)
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.status, 'pending')
    
    def test_contributor_cannot_edit_other_users_posts(self):
        """Test that contributor cannot edit posts by other users."""
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )
        
        post = Post.objects.create(
            title='Other User Post',
            slug='other-user-post',
            content='Content',
            category=self.category,
            author=other_user,
            status='draft'
        )
        
        response = self.client.get(reverse('core:submit_post_edit', args=[post.id]))
        # Should redirect with error message
        self.assertEqual(response.status_code, 302)


class PostStatusWorkflowTest(TestCase):
    """Test post status workflow (draft → pending → approved)."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='contributor',
            email='contributor@example.com',
            password='testpass123'
        )
        self.contributor_group = Group.objects.get_or_create(name=CONTRIBUTOR_GROUP)[0]
        self.user.groups.add(self.contributor_group)
        
        self.category = Category.objects.create(
            name='Housing',
            slug='housing'
        )
        
        self.client.login(username='contributor', password='testpass123')
    
    def test_post_starts_as_draft(self):
        """Test that new post starts as draft."""
        post = Post.objects.create(
            title='Draft Post',
            slug='draft-post',
            content='Content',
            category=self.category,
            author=self.user,
            status='draft'
        )
        
        self.assertEqual(post.status, 'draft')
        self.assertIsNone(post.published_at)
    
    def test_post_can_be_submitted_for_review(self):
        """Test that post can be changed from draft to pending."""
        post = Post.objects.create(
            title='Draft Post',
            slug='draft-post',
            content='Content',
            category=self.category,
            author=self.user,
            status='draft'
        )
        
        # Update to pending
        post.status = 'pending'
        post.save()
        
        self.assertEqual(post.status, 'pending')
        self.assertIsNone(post.published_at)
    
    def test_post_approved_sets_published_at(self):
        """Test that when post is approved, published_at is set."""
        post = Post.objects.create(
            title='Pending Post',
            slug='pending-post',
            content='Content',
            category=self.category,
            author=self.user,
            status='pending'
        )
        
        # Approve post
        post.status = 'approved'
        post.save()
        
        self.assertEqual(post.status, 'approved')
        self.assertIsNotNone(post.published_at)


class AdminApprovalTest(TestCase):
    """Test admin approving a post."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpass123',
            is_staff=True,
            is_superuser=True
        )
        
        self.contributor = User.objects.create_user(
            username='contributor',
            email='contributor@example.com',
            password='testpass123'
        )
        self.contributor_group = Group.objects.get_or_create(name=CONTRIBUTOR_GROUP)[0]
        self.contributor.groups.add(self.contributor_group)
        
        self.category = Category.objects.create(
            name='Housing',
            slug='housing'
        )
        
        self.pending_post = Post.objects.create(
            title='Pending Post',
            slug='pending-post',
            content='Content',
            category=self.category,
            author=self.contributor,
            status='pending'
        )
        
        self.client.login(username='admin', password='adminpass123')
    
    def test_admin_can_access_dashboard(self):
        """Test that admin can access dashboard."""
        response = self.client.get(reverse('core:dashboard'))
        self.assertEqual(response.status_code, 200)
    
    def test_admin_can_see_pending_posts(self):
        """Test that admin can see pending posts in dashboard."""
        response = self.client.get(reverse('core:dashboard'))
        
        self.assertIn('pending_posts', response.context)
        self.assertIn(self.pending_post, response.context['pending_posts'])
    
    def test_admin_can_approve_post(self):
        """Test that admin can approve a pending post."""
        response = self.client.post(
            reverse('core:approve_post', args=[self.pending_post.id])
        )
        
        self.assertEqual(response.status_code, 302)  # Redirect after approval
        
        # Refresh from database
        self.pending_post.refresh_from_db()
        self.assertEqual(self.pending_post.status, 'approved')
        self.assertIsNotNone(self.pending_post.published_at)
    
    def test_admin_can_reject_post(self):
        """Test that admin can reject a pending post."""
        response = self.client.post(
            reverse('core:reject_post', args=[self.pending_post.id])
        )
        
        self.assertEqual(response.status_code, 302)  # Redirect after rejection
        
        # Refresh from database
        self.pending_post.refresh_from_db()
        self.assertEqual(self.pending_post.status, 'rejected')


class ApprovedPostsVisibilityTest(TestCase):
    """Test that approved posts are visible in public pages."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='contributor',
            email='contributor@example.com',
            password='testpass123'
        )
        
        self.category = Category.objects.create(
            name='Housing',
            slug='housing'
        )
        
        # Create posts with different statuses
        self.approved_post = Post.objects.create(
            title='Approved Post',
            slug='approved-post',
            content='This is an approved post.',
            category=self.category,
            author=self.user,
            status='approved'
        )
        
        self.pending_post = Post.objects.create(
            title='Pending Post',
            slug='pending-post',
            content='This is a pending post.',
            category=self.category,
            author=self.user,
            status='pending'
        )
        
        self.draft_post = Post.objects.create(
            title='Draft Post',
            slug='draft-post',
            content='This is a draft post.',
            category=self.category,
            author=self.user,
            status='draft'
        )
    
    def test_approved_posts_visible_on_home(self):
        """Test that approved posts are visible on home page."""
        response = self.client.get(reverse('core:home'))
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('latest_posts', response.context)
        
        # Only approved posts should be in latest_posts
        latest_posts = response.context['latest_posts']
        self.assertIn(self.approved_post, latest_posts)
        self.assertNotIn(self.pending_post, latest_posts)
        self.assertNotIn(self.draft_post, latest_posts)
    
    def test_approved_posts_visible_in_category(self):
        """Test that approved posts are visible in category listing."""
        response = self.client.get(
            reverse('core:category_list', args=[self.category.slug])
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('posts', response.context)
        
        # Only approved posts should be visible to non-authenticated users
        posts = response.context['posts']
        self.assertIn(self.approved_post, posts)
        self.assertNotIn(self.pending_post, posts)
        self.assertNotIn(self.draft_post, posts)
    
    def test_approved_post_detail_accessible(self):
        """Test that approved post detail page is accessible."""
        response = self.client.get(
            reverse('core:post_detail', args=[self.approved_post.slug])
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['post'], self.approved_post)
    
    def test_pending_post_detail_not_accessible_to_anonymous(self):
        """Test that pending post detail is not accessible to anonymous users."""
        response = self.client.get(
            reverse('core:post_detail', args=[self.pending_post.slug])
        )
        
        # Should redirect to login or home
        self.assertIn(response.status_code, [302, 403])
    
    def test_draft_post_detail_not_accessible_to_anonymous(self):
        """Test that draft post detail is not accessible to anonymous users."""
        response = self.client.get(
            reverse('core:post_detail', args=[self.draft_post.slug])
        )
        
        # Should redirect to login or home
        self.assertIn(response.status_code, [302, 403])

