from django.test import TestCase, Client
from django.urls import reverse
from .models import Movie


class MovieFilterTest(TestCase):

    def setUp(self):
        self.client = Client()
        Movie.objects.create(name="Avengers", genre="action", language="english", rating=8.5, cast="RDJ", image="movies/test.jpg")
        Movie.objects.create(name="Pushpa", genre="action", language="hindi", rating=7.5, cast="Allu Arjun", image="movies/test.jpg")
        Movie.objects.create(name="Titanic", genre="romance", language="english", rating=9.0, cast="DiCaprio", image="movies/test.jpg")

    def test_genre_filter(self):
        response = self.client.get(reverse('movie_list') + '?genre=action')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['total_count'], 2)

    def test_language_filter(self):
        response = self.client.get(reverse('movie_list') + '?language=english')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['total_count'], 2)

    def test_combined_filter(self):
        response = self.client.get(reverse('movie_list') + '?genre=action&language=hindi')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['total_count'], 1)

    def test_empty_results(self):
        response = self.client.get(reverse('movie_list') + '?genre=horror')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['total_count'], 0)

    def test_search(self):
        response = self.client.get(reverse('movie_list') + '?search=pushpa')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['total_count'], 1)