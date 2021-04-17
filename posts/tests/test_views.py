# posts/tests/test_views.py
import datetime as dt
import shutil
import tempfile
import time

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.models import Follow, Group, Post

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создаем временную папку для медиа-файлов;
        # на момент теста медиа папка будет переопределена
        # создаем файл с картинкой
        small_gif = (
            b"\x47\x49\x46\x38\x39\x61\x02\x00"
            b"\x01\x00\x80\x00\x00\x00\x00\x00"
            b"\xFF\xFF\xFF\x21\xF9\x04\x00\x00"
            b"\x00\x00\x00\x2C\x00\x00\x00\x00"
            b"\x02\x00\x01\x00\x00\x02\x02\x0C"
            b"\x0A\x00\x3B"
        )
        uploaded = SimpleUploadedFile(
            name="small.gif",
            content=small_gif,
            content_type="image/gif"
        )
        # Создадим запись в БД
        Group.objects.create(
            title="Тестовая группа",
            slug="test-slug",
            description="Тестовое описание группы"
        )
        Group.objects.create(
            title="Тестовая группа 2",
            slug="test-slug-2",
            description="Тестовое описание группы 2"
        )
        Post.objects.create(
            text="Текст",
            group_id=1,
            author_id=1,
            image=uploaded
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        # Создаем авторизованный клиент
        self.user = User.objects.create_user(
            username="StasBasov",
            first_name="Stas Basov")
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        # Создаем второго авторизованного пользователя
        self.user_2 = User.objects.create_user(username="BasStasov")
        self.authorized_client_2 = Client()
        self.authorized_client_2.force_login(self.user_2)

    # Проверка словаря контекста главной страницы (в нём передаётся список
    # постов)
    def test_home_page_shows_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse("posts:index"))
        # Взяли первый элемент из списка и проверили, что его содержание
        # совпадает с ожидаемым
        first_post = response.context["page"][0]
        self.assertEqual(first_post.text, "Текст")
        self.assertEqual(type(first_post.pub_date), type(dt.datetime.now()))
        self.assertEqual(first_post.author.get_full_name(), "Stas Basov")
        self.assertEqual(first_post.image, "posts/small.gif")

    # Проверка паджинатора на количество постов на одну страницу
    def test_paginator_returns_needed_count_posts(self):
        posts_list = [Post(text=f"Текст{i}", author_id=1) for i in range(12)]
        Post.objects.bulk_create(posts_list)
        response = self.authorized_client.get(reverse("posts:index"))
        paginator = response.context["page"]
        self.assertEqual(len(paginator), 10)

    # Проверка словаря контекста страницы создания поста (в нём передаётся
    # форма)
    def test_new_post_shows_correct_context(self):
        """Шаблон new_post при создании нового поста
        сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse("posts:new-post"))
        # Словарь ожидаемых типов полей формы:
        # указываем, объектами какого класса должны быть поля формы
        form_fields = {
            "text": forms.fields.CharField,
            # При создании формы поля модели типа TextField
            # преобразуются в CharField с виджетом forms.Textarea
            "group": forms.fields.ChoiceField,
            "image": forms.fields.ImageField,
        }

        # Проверяем, что типы полей формы в словаре context
        # соответствуют ожиданиям
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context["form"].fields[value]
                # Проверяет, что поле формы является экземпляром
                # указанного класса
                self.assertIsInstance(form_field, expected)

    # Проверяем, что словарь context страницы group/test-slug
    # содержит ожидаемые значения
    def test_group_detail_pages_show_correct_context(self):
        """Шаблон group сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse("posts:group-detail", kwargs={"slug": "test-slug"}))
        first_post = response.context["page"][0]
        self.assertEqual(first_post.text, "Текст")
        self.assertEqual(first_post.author.get_full_name(),
                         "Stas Basov")
        self.assertEqual(first_post.group.title, "Тестовая группа")
        self.assertEqual(first_post.image.name, "posts/small.gif")
        self.assertEqual(type(first_post.pub_date), type(dt.datetime.now()))

    def test_post_not_in_other_group_detail_page_context(self):
        """Пост из первой группы не попал на страницу второй группы"""
        response = self.authorized_client.get(
            reverse("posts:group-detail", kwargs={"slug": "test-slug-2"}))
        self.assertEqual(len(response.context["page"]), 0)

# Проверка словаря контекста страницы редактирования поста (в нём передаётся
    # форма)
    def test_post_edit_shows_correct_context(self):
        """Шаблон new_post при редактиовании поста
         сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse("posts:post-edit",
                    kwargs={"username": self.user.username, "post_id": 1}))
        form_fields = {
            "text": forms.fields.CharField,
            "group": forms.fields.ChoiceField,
            "image": forms.fields.ImageField,
        }
        # Проверяем, что типы полей формы в словаре context
        # соответствуют ожиданиям
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context["form"].fields[value]
                # Проверяет, что поле формы является экземпляром
                # указанного класса
                self.assertIsInstance(form_field, expected)

# Проверка словаря контекста страницы профайла пользователя
# (в нём передаётся список постов)
    def test_profile_shows_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            "posts:profile",
            kwargs={"username": self.user.username}))
        # Взяли первый элемент из списка и проверили, что его содержание
        # совпадает с ожидаемым
        first_post = response.context["page"][0]
        self.assertEqual(first_post.text, "Текст")
        self.assertEqual(first_post.author.get_full_name(),
                         "Stas Basov")
        self.assertEqual(first_post.group.title, "Тестовая группа")
        self.assertEqual(first_post.image.name, "posts/small.gif")
        self.assertEqual(type(first_post.pub_date), type(dt.datetime.now()))

    # Проверяем, что словарь context страницы /<username>/<post_id>/
    # содержит ожидаемые значения
    def test_username_post_id_pages_show_correct_context(self):
        """Шаблон post сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse("posts:post", kwargs={
                "username": self.user.username,
                "post_id": 1}))
        self.assertEqual(response.context["post"].text, "Текст")
        self.assertEqual(response.context["author"].get_full_name(),
                         "Stas Basov")
        self.assertEqual(response.context["post_count"], 1)

    def test_cache_index_page(self):
        """Главная страница кэшируется каждые 20 секунд"""
        first_response = self.authorized_client.get(reverse("posts:index"))
        Post.objects.create(
            text="Текст проверка кэша",
            group_id=1,
            author_id=1,
        )
        second_response = self.authorized_client.get(reverse("posts:index"))
        time.sleep(21)
        third_response = self.authorized_client.get(reverse("posts:index"))
        self.assertEqual(first_response.content, second_response.content)
        self.assertNotEqual(second_response.content, third_response.content)

    def test_follow_view_working(self):
        """Проверим возможность подписки на другого
        пользователя"""
        # Проверяем отсутствие записей в таблице БД Follow
        self.assertFalse(Follow.objects.all())
        # Подписываем StasBasov на BasStasov
        self.authorized_client.get(
            reverse("posts:profile_follow",
                    kwargs={"username": "BasStasov"}))
        # Проверяем наличие записей в таблице БД Follow
        self.assertTrue(Follow.objects.all())

    def test_unfollow_view_working(self):
        """Проверим возможность отписки от автора"""
        # Проверяем отсутствие записей в таблице БД Follow
        self.assertFalse(Follow.objects.all())
        # Подписываем StasBasov на BasStasov
        self.authorized_client.get(
            reverse("posts:profile_follow",
                    kwargs={"username": "BasStasov"}))
        # Отписываем StasBasov от BasStasov
        self.authorized_client.get(
            reverse("posts:profile_unfollow",
                    kwargs={"username": "BasStasov"}))
        # Проверяем отсутствие записей в таблице БД Follow
        self.assertFalse(Follow.objects.all())

    def test_new_post_in_followers_follow_index_page(self):
        """В ленте подписавшегося пользователя новый пост
        появляется"""
        # Проверим отсутствие постов в ленте у BasStasov
        response = self.authorized_client_2.get(
            reverse("posts:follow_index"))
        self.assertFalse(response.context["page"])
        # Подписываем BasStasov на StasBasov
        self.authorized_client_2.get(
            reverse("posts:profile_follow",
                    kwargs={"username": "StasBasov"}))
        # Создадим пост с авторством StasBasov
        post = Post.objects.create(text="Проверка ленты", author_id=1)
        # Проверим наличие нового поста в ленте подписавшегося
        response = self.authorized_client_2.get(
            reverse("posts:follow_index"))
        self.assertIn(post, response.context["page"])

    def test_new_post_not_in_not_followers_follow_index_page(self):
        """В ленте неподписавшегося пользователя новый пост
        не появляется"""
        # Проверим отсутствие постов в ленте у BasStasov
        response = self.authorized_client_2.get(
            reverse("posts:follow_index"))
        self.assertFalse(response.context["page"])
        # Создадим пост с авторством StasBasov
        post = Post.objects.create(text="Проверка ленты", author_id=1)
        # Проверим отстутствие нового поста в ленте подписавшегося
        response = self.authorized_client_2.get(
            reverse("posts:follow_index"))
        self.assertNotIn(post, response.context["page"])

    def test_add_comment_page_is_not_avialable_for_anonimous(self):
        """Недоступность комментирования невторизованному пользователю"""
        self.anonimous_client = Client()
        # Недоступность страницы комментирования анонимному пользователю
        response = self.anonimous_client.get(
            reverse("posts:add-comment",
                    kwargs={"username": "StasBasov", "post_id": 1}))
        self.assertNotEqual(response.status_code, 200)

    def test_add_cooment_page_is_avialable_for_authorized(self):
        """Доступность комментирования авторизованному пользователю"""
        # Доступность комментирования авторизованному пользователю
        response = self.authorized_client.get(
            reverse("posts:add-comment",
                    kwargs={"username": "StasBasov", "post_id": 1}))
        self.assertEqual(response.status_code, 200)
