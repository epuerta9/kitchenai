from allauth.account.forms import SignupForm as BaseSignupForm
from django import forms

class KitchenAISignupForm(BaseSignupForm):
    # Remove all problematic clean methods
    clean_email2 = None
    clean_username = None

    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                'class': 'input input-bordered w-fulla',
                'placeholder': 'Email address'
            }
        )
    )
    
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(
            attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'Password'
            }
        )
    )
    
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(
            attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'Confirm Password'
            }
        )
    )

    field_order = ['email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove all unused fields
        self.fields = {
            'email': self.fields['email'],
            'password1': self.fields['password1'],
            'password2': self.fields['password2'],
        }

    def save(self, request):
        user = super().save(request)
        user.role = 'admin'  # Set role to admin by default
        user.save()
        return user

    def clean(self):
        cleaned_data = super().clean()
        # Generate username from email if needed
        if 'email' in cleaned_data:
            cleaned_data['username'] = cleaned_data['email'].split('@')[0]
        return cleaned_data
