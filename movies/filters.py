from django import forms
from .models import Movie


class MovieFilterForm(forms.Form):
    search = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control form-control-lg',
        'placeholder': 'Search movies...'
    }))
    genre = forms.MultipleChoiceField(
        required=False,
        choices=Movie.GENRE_CHOICES,
        widget=forms.CheckboxSelectMultiple()
    )
    language = forms.MultipleChoiceField(
        required=False,
        choices=Movie.LANGUAGE_CHOICES,
        widget=forms.CheckboxSelectMultiple()
    )
    sort_by = forms.ChoiceField(
        required=False,
        choices=[
            ('', 'Default'),
            ('rating', 'Rating: High to Low'),
            ('-rating', 'Rating: Low to High'),
            ('name', 'Name: A to Z'),
            ('-name', 'Name: Z to A'),
        ]
    )