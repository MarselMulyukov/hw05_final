from django.test import Client, TestCase
from django.urls import reverse


class StaticViewsTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_about_urls_uses_correct_templates(self):
        """Проверка используемых шаблонов адресами /about/author/
        и /about/tech/"""
        templates = {'about:author': 'about/author.html',
                     'about:tech': 'about/tech.html'}
        for value, expected in templates.items():
            with self.subTest():
                self.assertTemplateUsed(
                    self.guest_client.get(reverse(value)),
                    expected)
