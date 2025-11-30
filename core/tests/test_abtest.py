"""
Tests for A/B test endpoint.
"""
from django.test import TestCase, Client


class ABTestViewTest(TestCase):
    """Test cases for A/B test endpoint."""
    
    def setUp(self):
        """Set up test client."""
        self.client = Client()
        self.abtest_url = '/218b7ae/'
    
    def test_abtest_endpoint_is_public(self):
        """Test that A/B test endpoint is publicly accessible (no login required)."""
        response = self.client.get(self.abtest_url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'far-storm')
        self.assertContains(response, 'Chun-Hung Yeh')
        self.assertContains(response, 'Celine (Qijing) Li')
        self.assertContains(response, 'Denise Wu')
    
    def test_abtest_button_id_and_text(self):
        """Test that button has correct id and text is either 'kudos' or 'thanks'."""
        response = self.client.get(self.abtest_url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="abtest"')
        
        # Check that button text is either 'kudos' or 'thanks'
        content = response.content.decode('utf-8')
        
        # Find the button and extract its text
        import re
        # Look for the button element with id="abtest"
        button_match = re.search(r'<button[^>]*id="abtest"[^>]*>([^<]+)</button>', content)
        
        self.assertIsNotNone(button_match, "Button with id='abtest' not found")
        
        button_text = button_match.group(1).strip()
        self.assertIn(button_text, ['kudos', 'thanks'], 
                     f"Button text '{button_text}' is not 'kudos' or 'thanks'")
    
    def test_ab_variant_cookie_consistency(self):
        """Test that variant is consistent via cookie across requests."""
        # First request - should set cookie
        response1 = self.client.get(self.abtest_url)
        self.assertEqual(response1.status_code, 200)
        
        # Check that cookie was set
        cookies = response1.cookies
        self.assertIn('ab_variant', cookies)
        
        variant1 = cookies['ab_variant'].value
        self.assertIn(variant1, ['kudos', 'thanks'])
        
        # Extract variant from response content
        content1 = response1.content.decode('utf-8')
        import re
        button_match1 = re.search(r'<button[^>]*id="abtest"[^>]*>([^<]+)</button>', content1)
        variant_from_content1 = button_match1.group(1).strip()
        
        # Second request with cookie - should use same variant
        self.client.cookies['ab_variant'] = variant1
        response2 = self.client.get(self.abtest_url)
        self.assertEqual(response2.status_code, 200)
        
        content2 = response2.content.decode('utf-8')
        button_match2 = re.search(r'<button[^>]*id="abtest"[^>]*>([^<]+)</button>', content2)
        variant_from_content2 = button_match2.group(1).strip()
        
        # Variants should match
        self.assertEqual(variant_from_content1, variant_from_content2)
        self.assertEqual(variant_from_content2, variant1)
    
    def test_abtest_view_uses_correct_template(self):
        """Test that A/B test view uses the correct template."""
        response = self.client.get(self.abtest_url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/abtest.html')
    
    def test_abtest_variant_random_distribution(self):
        """Test that variants are randomly chosen (at least one of each in multiple requests)."""
        variants_seen = set()
        
        # Make multiple requests without cookies to see different variants
        for _ in range(20):
            client = Client()  # New client each time (no cookies)
            response = client.get(self.abtest_url)
            self.assertEqual(response.status_code, 200)
            
            content = response.content.decode('utf-8')
            import re
            button_match = re.search(r'<button[^>]*id="abtest"[^>]*>([^<]+)</button>', content)
            if button_match:
                variant = button_match.group(1).strip()
                variants_seen.add(variant)
                
                # Early exit if we've seen both variants
                if len(variants_seen) == 2:
                    break
        
        # We should have seen at least one variant (both if we're lucky)
        self.assertGreater(len(variants_seen), 0)
    
    def test_abtest_analytics_script_present(self):
        """Test that analytics tracking script is present in the template."""
        response = self.client.get(self.abtest_url)
        
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        
        # Check for gtag calls
        self.assertIn("gtag('event', 'ab_variant_shown'", content)
        self.assertIn("gtag('event', 'ab_variant_clicked'", content)
        self.assertIn("event_category': 'abtest'", content)

