from django.contrib.auth.models import AbstractUser
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
)
from django.db import models
from django.utils import timezone

from .constants import (
    CHAR_FIELD_LIMIT,
    CODE_LENGTH,
    EMAIL_LENGTH,
    MAX_TITLE_SCORE,
    MIN_TITLE_SCORE,
    ROLE_LENGTH,
    SLUG_FIELD_LIMIT,
    SYMBOLS_LIMIT,
    USERNAME_LENGTH,
)
from .validators import validate_username


class User(AbstractUser):
    USER = 'user'
    ADMIN = 'admin'
    MODERATOR = 'moderator'

    ROLE_CHOICES = [
        (USER, USER),
        (ADMIN, ADMIN),
        (MODERATOR, MODERATOR),
    ]
    role = models.CharField(
        'роль', choices=ROLE_CHOICES, default=USER, max_length=ROLE_LENGTH
    )
    confirmation_code = models.CharField(
        'код подтверждения',
        max_length=CODE_LENGTH,
        blank=False,
        default='012345',
    )
    bio = models.TextField(
        'биография',
        blank=True,
    )
    email = models.EmailField('почта', max_length=EMAIL_LENGTH, unique=True)
    username = models.CharField(
        max_length=USERNAME_LENGTH,
        verbose_name='имя пользователя',
        unique=True,
        validators=(validate_username,),
    )

    @property
    def is_user(self):
        return self.role == self.USER

    @property
    def is_admin(self):
        return self.role == self.ADMIN

    @property
    def is_moderator(self):
        return self.role == self.MODERATOR

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['username']
        constraints = [
            models.UniqueConstraint(
                fields=('username', 'email'), name='usrname_email_constraint'
            ),
        ]

    def __str__(self):
        return self.username


class Genre(models.Model):
    """Модель для имени и описания жанра."""

    name = models.CharField(
        max_length=CHAR_FIELD_LIMIT, verbose_name='Название'
    )
    slug = models.SlugField(
        max_length=SLUG_FIELD_LIMIT, unique=True, verbose_name='Слаг'
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.name


class Category(models.Model):
    """Модель для имени и описания категории."""

    name = models.CharField(
        max_length=CHAR_FIELD_LIMIT, verbose_name='Название'
    )
    slug = models.SlugField(
        max_length=SLUG_FIELD_LIMIT, unique=True, verbose_name='Слаг'
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Title(models.Model):
    """Модель, описывающая произведение."""

    name = models.CharField(
        max_length=CHAR_FIELD_LIMIT, verbose_name='Название'
    )
    year = models.PositiveSmallIntegerField(
        verbose_name='Год создания',
        validators=[MaxValueValidator(timezone.now().year)],
        db_index=True,
    )
    description = models.TextField(
        null=True, blank=True, verbose_name='Описание'
    )
    genre = models.ManyToManyField(
        Genre,
        related_name='genres',
        through='TitleGenres',
        verbose_name='Жанр',
    )
    category = models.ForeignKey(
        Category,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='categories',
        verbose_name='Категория',
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'

    def __str__(self):
        return f'{self.name}, {self.year}, {self.description[:SYMBOLS_LIMIT]}'


class TitleGenres(models.Model):
    title = models.ForeignKey(Title, on_delete=models.CASCADE)
    genre = models.ForeignKey(
        Genre, null=True, blank=True, on_delete=models.SET_NULL
    )


class Review(models.Model):
    """Настройки модели Отзывов."""

    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='reviews'
    )
    title = models.ForeignKey(
        Title, on_delete=models.CASCADE, related_name='reviews'
    )
    text = models.TextField()
    pub_date = models.DateTimeField(
        'Дата добавления', auto_now_add=True, db_index=True
    )
    score = models.PositiveSmallIntegerField(
        default=0,
        validators=[
            MinValueValidator(MIN_TITLE_SCORE),
            MaxValueValidator(MAX_TITLE_SCORE),
        ],
    )

    class Meta:
        """Метаданные модели отзывов."""

        ordering = ('pub_date',)
        verbose_name = 'отзыв'
        verbose_name_plural = 'Отзывы'
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'title'], name='unique_author_title'
            )
        ]

    def __str__(self):
        """Возвращает строковое представление объекта."""
        return self.text


class Comments(models.Model):
    """Настройки модели Comment."""

    author = models.ForeignKey(User, on_delete=models.CASCADE)
    review = models.ForeignKey(Review, on_delete=models.CASCADE)
    text = models.TextField()
    pub_date = models.DateTimeField(
        'Дата добавления', auto_now_add=True, db_index=True
    )

    class Meta:
        """Метаданные модели комментариев."""

        default_related_name = 'comments'
        ordering = ('pub_date',)
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        """Возвращает строковое представление объекта."""
        return self.text
