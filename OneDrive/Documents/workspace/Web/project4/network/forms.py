from django import forms
from .models import Post

class PostForm(forms.ModelForm):
    text = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Enter text here', 'id': 'floatingTextarea'}),
        required = False
    )

    image = forms.ImageField(widget=forms.FileInput(
        attrs={'class': 'form-control image_btn', 'id': 'image_uploads', 'name': 'image_uploads'}),
        required=False,
    )
    class Meta:
        model = Post
        fields = ['text', 'image']
        
    