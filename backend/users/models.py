from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator


class User(AbstractUser):
    email = models.EmailField(
        max_length=150,
        unique=True,
        verbose_name='E-mail',
    )
    username = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Login',
        validators=[
            RegexValidator(
                regex=r'^[\w-]*$',
                message='Use characters from this list [a-zA-Z0-9_-]',
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
        ordering = ('-id',)
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.username
