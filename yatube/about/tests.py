from django.test import TestCase, Client
from django.urls import reverse

from http import HTTPStatus


class StaticPagesURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_about_urls_exists_at_desired_location(self):
        """Проверка доступности статических адресов."""
        urls_static = [reverse('about:tech'), reverse('about:author')]
        for reverse_name in urls_static:
            with self.subTest(address=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_about_urld_uses_correct_template(self):
        """Проверка статических шаблонов для адресов."""
        templates_url_names = {
            reverse('about:tech'): 'about/tech.html',
            reverse('about:author'): 'about/author.html'
        }
        for reverse_name, template in templates_url_names.items():
            with self.subTest(address=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
