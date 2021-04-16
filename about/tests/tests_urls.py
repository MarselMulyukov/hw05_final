from django.test import Client, TestCase
from django.urls import reverse


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_about_urls_exists_at_desired_location(self):
        """Проверка доступности адресов /about/author/ и /about/tech/
        при помощи конструкции reverse(name)."""
        urls_accesibility = {'about:tech': 200, 'about:author': 200}
        for value, expected in urls_accesibility.items():
            with self.subTest():
                self.assertEqual(
                    self.guest_client.get(reverse(value)).status_code,
                    expected)
