from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    title = models.CharField(verbose_name="Группа", max_length=200,
                             help_text="Выберите группу")
    slug = models.SlugField("Адрес URL", unique=True)
    description = models.TextField("Описание группы")

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField("Текст", help_text="Текст статьи")
    pub_date = models.DateTimeField("Дата публикации", auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name="posts")
    group = models.ForeignKey(Group, verbose_name="Группа",
                              on_delete=models.SET_NULL,
                              blank=True, null=True, related_name="posts",
                              help_text="Выберите группу")
    image = models.ImageField(verbose_name="Изображение",
                              help_text="Загрузить изображение",
                              upload_to="posts/",
                              blank=True,
                              null=True)

    def __str__(self):
        return self.text[:15]

    class Meta:
        ordering = ("-pub_date",)


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE,
                             related_name="comments")
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name="comments")
    text = models.TextField("Комментарий", help_text="Текст комментария")
    created = models.DateTimeField("Дата и время комментария",
                                   auto_now_add=True)

    def __str__(self):
        return self.text[:15]

    class Meta:
        ordering = ("-created",)


class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name="follower")
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name="following")

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "author"],
                                    name="unique_following"), ]
