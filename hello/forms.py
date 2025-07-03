# text_app/forms.py
from django import forms
from .models import TextDescription

class TextDescriptionForm(forms.ModelForm):
    class Meta:
        model = TextDescription
        fields = ['title', 'description']