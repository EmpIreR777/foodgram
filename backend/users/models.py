from django.contrib.auth.models import AbstractUser
from django.db import models

from .validators import username_validator


class User(AbstractUser):
    """Модель пользователя."""

    email = models.EmailField(
        'E-mail', max_length=254,
        unique=True, help_text='Введите email пользователя')
    username = models.CharField(
        'Логин', max_length=150,
        unique=True, 
        validators=[username_validator],
        help_text='Введите логин поьзователя')
    first_name = models.CharField(
        'Имя', max_length=150,
        help_text='Введите имя пользователя')
    last_name = models.CharField(
        'Фамилия', max_length=150,
        help_text='Введите фамилию пользователя')
    avatar = models.ImageField(
        'Аватар', upload_to='media/avatar',
        null=True, blank=True, default=None)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name', 'password')

    class Meta:
        ordering = ('username', 'id')
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Follow(models.Model):
    """Модель подписок."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Подписан',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'following'], name='unique_user',
                violation_error_message='Уже подписан.'
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F('following')),
                name='not_yourself_follow',
                violation_error_message='Нельзя подписаться на себя.',
            ),
        ]
        ordering = ('user', 'following', 'id')
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f'{self.user} подписан на {self.following}'
