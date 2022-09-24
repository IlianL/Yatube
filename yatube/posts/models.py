from django.contrib.auth import get_user_model
from django.db import models

TEXT_PREVIEW_CHARS: int = 15

User = get_user_model()


class Group(models.Model):
    """Таблица для групп."""
    title = models.CharField(
        max_length=200, verbose_name='Название группы',
        help_text='Название вашей груупы будет видно всем пользователям'
    )
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(
        blank=True, null=True, verbose_name='Описание группы',
        help_text='Чему будет посвящена ваша группа?'
    )

    def __str__(self):
        return self.title


class Post(models.Model):
    """Таблица для постов."""
    text = models.TextField(
        verbose_name="Текст поста",
        help_text='Введите текст поста'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата публикации"
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name="Автор"
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        related_name='posts',
        blank=True,
        null=True,
        verbose_name='Название группы',
        help_text='Группа, к которой будет относиться пост'
    )
    image = models.ImageField(
        upload_to='posts/',
        blank=True,
        verbose_name='Картинка',
        help_text='Загрузите картинку'

    )

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def __str__(self):
        return self.text[:TEXT_PREVIEW_CHARS] + '...'


class Comment(models.Model):
    text = models.TextField(
        verbose_name="Текст комментария",
        help_text='Введите текст комментария'
    )
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата комментария"
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name="Автор"
    )
    post = models.ForeignKey(
        Post,
        related_name='comments',
        on_delete=models.CASCADE
    )

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return f'Комментарий {self.name}, пост - {self.post}'


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        related_name='follower',
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    author = models.ForeignKey(
        User,
        related_name='following',
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )

    class Meta:
        verbose_name_plural = 'Подписки'
        verbose_name = 'Подписка'
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'user'], name='unique_follow'
            )
        ]

    def __str__(self):
        return f"Последователь: '{self.user}', автор: '{self.author}'"
