"""
Forms for Yale Newcomer Survival Guide.

Contains forms for post submission and editing.
"""

from django import forms
from .models import Post, Category


class PostForm(forms.ModelForm):
    """Form for contributors to submit/edit posts."""
    
    class Meta:
        model = Post
        fields = ['title', 'slug', 'content', 'category', 'status']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 15}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        """Initialize form with user and restrict status choices for contributors."""
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Contributors can only set status to draft or pending
        if self.user and not self.user.is_staff:
            self.fields['status'].choices = [
                ('draft', 'Draft'),
                ('pending', 'Pending Review'),
            ]
            # Set default to pending for new posts
            if not self.instance.pk:
                self.fields['status'].initial = 'pending'

