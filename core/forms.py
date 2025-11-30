"""
Forms for Yale Newcomer Survival Guide.

Contains forms for post submission, editing, and user registration.
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Post


class UserRegistrationForm(UserCreationForm):
    """User registration form with optional email field."""
    email = forms.EmailField(required=False, help_text="Optional. Used for account recovery.")
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to form fields
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class PostForm(forms.ModelForm):
    """Form for contributors to submit/edit posts."""
    
    class Meta:
        model = Post
        fields = ['title', 'content', 'category', 'status']  # Slug is auto-generated, not shown to contributors
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
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

