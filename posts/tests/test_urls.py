# posts/tests/test_urls.py
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Group.objects.create(
            title="Тестовая группа",
            description="Тестовое описание группы",
            slug="test-slug"
        )
        Post.objects.create(
            text="Тестовый текст",
            author_id=1
        )

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем пользователей
        self.user = User.objects.create_user(username="AndreyG")
        self.user_2 = User.objects.create_user(username="AndreyB")
        # Создаем второй клиент
        self.authorized_client = Client()
        self.authorized_client_2 = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(self.user)
        self.authorized_client_2.force_login(self.user_2)

    # Проверяем общедоступные страницы
    def test_posts_urls_exists_at_desired_location(self):
        """Проверка доступности неавторизованному пользователю
        адресов /, /group/test-slug/, /<username>/, /<username>/<post_id>/
        при помощи конструкции reverse(name)."""
        urls_accesibility = {"posts:index": None,
                             "posts:group-detail": {"slug": "test-slug"},
                             "posts:profile": {"username": "AndreyG"},
                             "posts:post": {"username": "AndreyG",
                                            "post_id": 1}}
        for name, kwargs in urls_accesibility.items():
            with self.subTest(value=name):
                self.assertEqual(
                    self.guest_client.get(reverse(name,
                                          kwargs=kwargs)).status_code, 200)

    # Проверяем доступность страницы редактирования поста
    # для автора поста
    def test_post_edit_url_exists_at_desired_location(self):
        """Страница /<username>/<post_id>/edit/
                       доступна автору поста."""
        response = self.authorized_client.get(reverse(
            "posts:post-edit",
            kwargs={"username": "AndreyG", "post_id": 1}))
        self.assertEqual(response.status_code, 200)

    # Проверяем доступность страниц для авторизованного пользователя
    def test_new_url_exists_at_desired_location(self):
        """Страница /new доступна авторизованному пользователю."""
        response = self.authorized_client.get(reverse("posts:new-post"))
        self.assertEqual(response.status_code, 200)

    def test_post_edit_url_redirect_not_author_to_post_view(self):
        """Страница по адресу /AndreyG/1/edit/ перенаправит не автора
        поста на страницу просмотра поста.
        """
        response = self.authorized_client_2.get(reverse(
            "posts:post-edit",
            kwargs={"username": "AndreyG", "post_id": 1}))
        url_redirected = reverse(
            "posts:post",
            kwargs={"username": "AndreyG", "post_id": 1})
        self.assertRedirects(response, url_redirected)

    # Проверяем редиректы для неавторизованного пользователя
    def test_new_url_redirect_anonymous_on_admin_login(self):
        """Страница по адресу /new перенаправит анонимного
        пользователя на страницу логина.
        """
        reversed_url = reverse('posts:new-post')
        response = self.guest_client.get(
            reversed_url,
            follow=True)
        url_login = reverse("login")
        self.assertRedirects(response,
                             f"{url_login}?next={reversed_url}")

    def test_post_edit_url_redirect_anonimous_user(self):
        """Страница по адресу /AndreyG/1/edit/ перенаправит анонимного
        пользователя на страницу логина.
        """
        reversed_url = reverse(
            "posts:post-edit",
            kwargs={"username": "AndreyG", "post_id": 1})
        response = self.guest_client.get(reversed_url, follow=True)
        url_login = reverse("login")
        self.assertRedirects(response, f"{url_login}?next={reversed_url}")

    # Проверка вызываемых шаблонов для каждого адреса
    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Шаблоны по адресам
        templates_url_names = [
            {"name": "posts:index",
             "kwargs": None,
             "template": "posts/index.html"},
            {"name": "posts:group-detail",
             "kwargs": {"slug": "test-slug"},
             "template": "posts/group.html"},
            {"name": "posts:new-post",
             "kwargs": None,
             "template": "posts/new_post.html"},
            {"name": "posts:post-edit",
             "kwargs": {"username": "AndreyG", "post_id": 1},
             "template": "posts/new_post.html"}
        ]
        for data_dict in templates_url_names:
            with self.subTest(value=data_dict["name"]):
                response = self.authorized_client.get(
                    reverse(
                        data_dict["name"],
                        kwargs=data_dict["kwargs"]))
                self.assertTemplateUsed(response, data_dict["template"])

    def test_not_set_page_calls_code_404(self):
        """Ненайденная страница дает код 404"""
        response = self.authorized_client.get(
            "/undefined/page/",
            exception=True)
        self.assertEqual(response.status_code, 404)
