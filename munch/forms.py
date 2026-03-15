from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Author,Entry

# The following class from Google, Gemini, "Django Author Identity", 02-28-2026
class AuthorUpdateForm(forms.ModelForm):
    class Meta:
        model = Author
        fields = ['displayName', 'description', 'github', 'profileImage']
        widgets = {
            'displayName': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 4, 
                'placeholder': 'Tell us about yourself...'
            }),
            
            'github': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://github.com/username'}),
            'profileImage': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://example.com/image.jpg'}),
        }

# The following class from Google, Gemini, "Django Author Identity", 02-28-2026
class SignupForm(UserCreationForm):
    # We include displayName here because it's in your REQUIRED_FIELDS
    class Meta(UserCreationForm.Meta):
        model = Author
        fields = ("username", "displayName", "github")

    def save(self, commit=True):
        author = super().save(commit=False)
        # Your model's save() method will automatically generate 
        # the FQID (id) using the UUID and host.
        if commit:
            author.save()
        return author
    
class EntryForm(forms.ModelForm):
    VISIBILITY_CHOICES = [('PUBLIC', 'Public'),('PRIVATE', 'Private'),('UNLISTED', 'Unlisted'),]
    CONTENT_TYPE_CHOICES = [
        ('text/plain', 'Plain Text'),
        ('text/markdown', 'Markdown'),
        ('image/png;base64', 'PNG Image'),
        ('image/jpeg;base64', 'JPEG Image'),
    ]

    visibility = forms.ChoiceField(choices=VISIBILITY_CHOICES)
    contentType = forms.ChoiceField(choices=CONTENT_TYPE_CHOICES)
    image = forms.ImageField(required=False, help_text='Upload an image (PNG or JPEG) :)')

    class Meta:
        model = Entry
        fields = ('title', 'description', 'contentType', 'content', 'visibility')
        labels = {
            'contentType': 'Content Type',
        }
        widgets = {
            'title': forms.TextInput(attrs={
                'placeholder': 'Enter title',
                'class': 'form-input'
            }),
            'description': forms.TextInput(attrs={
                'placeholder': 'Short description',
                'class': 'form-input'
            }),
            'content': forms.Textarea(attrs={
                'placeholder': 'Write your post here...',
                'rows': 6,
                'class': 'form-input'
            }),
        }

        
        
    

    