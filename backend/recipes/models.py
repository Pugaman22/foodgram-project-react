from colorfield.fields import ColorField
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Exists, OuterRef

User = get_user_model()


class Tag(models.Model):
    """Tags model."""
    name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='tag name',
    )
    colour = ColorField(
        unique=True,
        verbose_name='tag colour',
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name='tag slug',
    )

    class Meta:
        verbose_name_plural = 'Tags'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Ingredients model."""
    name = models.CharField(
        max_length=100,
        verbose_name='ingredient name',
    )
    measurement_unit = models.CharField(
        max_length=20,
        verbose_name='unit of measurement',
    )

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Ingredients'

    def __str__(self):
        return f'{self.name} - {self.measurement_unit}'


class RecipeManagerForRelatedFields(models.Manager):

    def get_queryset(self):
        return Recipe.objects.all().select_related(
                'author').prefetch_related('tags')

    def fill_favs_and_in_cart(self, user):
        if user.is_authenticated:
            favorited = Favorite.objects.filter(
                user=user,
                recipe=OuterRef('pk')
            )
            in_cart = PurchasingList.objects.filter(
                user=user,
                recipe=OuterRef('pk')
            )
            return self.get_queryset().annotate(
                is_favorited=Exists(favorited)).annotate(
                    is_in_shopping_cart=Exists(in_cart))

        else:
            return self.get_queryset()


class Recipe(models.Model):
    """Recipes model."""
    objects = models.Manager()
    objects_with_related_fields = RecipeManagerForRelatedFields()
    name = models.CharField(max_length=200,
                            verbose_name='recipe name',)
    description = models.TextField('recipe description',
                                   help_text='Write a description')
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='recipes',
        verbose_name='recipe author',
    )
    image = models.ImageField(
        'meal picture',
        upload_to='foodgram/images/',
    )
    cooking_time = models.SmallIntegerField(
        validators=[MinValueValidator(
            1,
            message='Minimum value is 1!',
        ),
            MaxValueValidator(
            1440,
            message='Maximum value is 1440 (24h)!'
        )
        ],
        help_text='Type cooking time using minutes.'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientsRecipe',
        related_name='recipes',
        verbose_name='Recipe ingredients',
    )
    tags = models.ManyToManyField(
        Tag,
        through='TagsRecipe',
        related_name='recipes',
        verbose_name='Recipe tags',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Publication date',
    )

    class Meta:
        ordering = ['-pub_date']
        verbose_name_plural = 'Recipes'

    def __str__(self):
        return self.name


class IngredientsRecipe(models.Model):
    """Model is linking recipe and ingredients."""
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredients_list',
        verbose_name='description'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredients_list',
        verbose_name='Recipe',
    )
    amount = models.SmallIntegerField(
        validators=[MinValueValidator(1, message='Minimaum value is 1!',)],
        verbose_name='Ingredient quantity',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('ingredient', 'recipe',),
                name='unique_ingredients_for_recipe'),
        ]
        verbose_name = 'List of ingredients for recipe'
        verbose_name_plural = 'List of ingredients for recipes'

    def __str__(self):
        return f'{self.ingredient} - {self.quantity}'


class TagsRecipe(models.Model):
    """Model is linking recipe and tags."""
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        related_name='tags_list',
        verbose_name='tag'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='tags_list',
        verbose_name='recipe',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('recipe', 'tag',),
                name='unique_tags_for_recipe',
            ),
        ]
        verbose_name = 'List of tags for recipe'
        verbose_name_plural = 'List of tags for recipes'

    def __str__(self):
        return f'{self.tag} - {self.recipe}'


class Favorite(models.Model):
    """Model of favorite recipes."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='рецепт',
    )

    class Meta:
        verbose_name = 'Favorite'
        verbose_name_plural = 'Favorites'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite'
            )
        ]


class PurchasingList(models.Model):
    """List of purchased recipes."""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='purchasing_list',
        verbose_name='purchasing recipe',
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='purchasing_list',
        verbose_name='purchasing user',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('recipe', 'user',),
                name='unique_shopping_pair',
            ),
        ]
        ordering = ('recipe',)
        verbose_name = 'Recipe for purchasing'
        verbose_name_plural = 'Recipes for purchasing'

    def __str__(self):
        return f'{self.recipe} - {self.user}'
