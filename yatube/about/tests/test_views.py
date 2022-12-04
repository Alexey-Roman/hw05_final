from django.test import TestCase


class URLTemplatesTest(TestCase):
    """Проверка шаблонов по url."""

    def test_temlate_use_url(self):
        url_template = (
            ('/about/author/', 'about/author.html'),
            ('/about/tech/', 'about/tech.html'),
        )

        for url, template in url_template:
            with self.subTest(url=url, temlate=template):
                response = self.client.get(url)
                self.assertTemplateUsed(response, template)
