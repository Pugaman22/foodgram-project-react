from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator


class User(AbstractUser):
    email = models.EmailField(
        max_length=254,
        unique=True,
        verbose_name='E-mail',
    )
    username = models.CharField(
        max_length=150,
        unique=True,
        verbose_name='Login',
        validators=[
            RegexValidator(
                regex=r'^[\w.@+-]+$',
                message='Use characters from this list [a-zA-Z0-9_-+.]',
            ),
        ]
    )
    first_name = models.CharField(
        max_length=150,
    )
    last_name = models.CharField(
        max_length=150,
    )
    password = models.CharField(
        max_length=150,
    )

    class Meta:
        ordering = ('username',)
        verbose_name_plural = 'Users'
        constraints = [
            models.UniqueConstraint(
                fields=['username', 'email'],
                name='unique_username_and_email'
            )
        ]

    def __str__(self):
        return self.username


class Subscription(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipe_author'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriber'
    )

    class Meta:
        verbose_name_plural = 'Subscriptions'
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'user'],
                name='unique_author_and_subscriber'
            )
        ]

    def __str__(self):
        return f'{self.user} subscribed on {self.author}'
