from django.test import TestCase

from posts.models import Group, Post, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(
            username="leo"
        )
        cls.group = Group.objects.create(
            title="Тестовая группа"
        )
        # Создаём тестовую запись в БД
        # и сохраняем ее в качестве переменной класса
        cls.post = Post.objects.create(
            text="Тестовый текст15",
            author_id=1,
        )

    def test_post_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        post = PostModelTest.post
        field_verboses = {
            "text": "Текст"
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected)

    def test_group_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        group = PostModelTest.group
        field_verboses = {
            "title": "Группа"
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    group._meta.get_field(value).verbose_name, expected)

    def test_post_help_text(self):
        """help_text в полях совпадает с ожидаемым."""
        post = PostModelTest.post
        field_help_texts = {
            "text": "Текст статьи"
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).help_text, expected)

    def test_group_help_text(self):
        """help_text в полях совпадает с ожидаемым."""
        group = PostModelTest.group
        field_help_texts = {
            "title": "Выберите группу"
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    group._meta.get_field(value).help_text, expected)

    def test_post__str__(self):
        """метод __str__ работает"""
        post = PostModelTest.post
        post__str__ = str(post)
        self.assertEquals(post__str__, 'Тестовый текст1')

    def test_group__str__(self):
        """метод __str__ работает"""
        group = PostModelTest.group
        group__str__ = str(group)
        self.assertEquals(group__str__, 'Тестовая группа')
