from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class StaticURLTest(TestCase):
    """Проверка статичных страниц."""

    def test_static_pages(self):
        static_urls = (
            '/about/author/',
            '/about/tech/'
        )
        for url in static_urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_static_pages_reverse(self):
        static_urls_reverse = (
            ('/about/author/', 'about:author'),
            ('/about/tech/', 'about:tech'),
        )
        for url, func_name in static_urls_reverse:
            with self.subTest(url=url):
                self.assertEqual(reverse(func_name), url)
