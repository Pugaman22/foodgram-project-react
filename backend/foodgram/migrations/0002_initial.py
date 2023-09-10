# Generated by Django 4.2.4 on 2023-09-07 18:48

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('foodgram', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipe',
            name='author',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='recipes', to=settings.AUTH_USER_MODEL, verbose_name='recipe author'),
        ),
        migrations.AddField(
            model_name='recipe',
            name='ingredients',
            field=models.ManyToManyField(related_name='recipes', through='foodgram.IngredientsRecipe', to='foodgram.ingredient', verbose_name='Recipe ingredients'),
        ),
        migrations.AddField(
            model_name='recipe',
            name='tags',
            field=models.ManyToManyField(related_name='recipes', through='foodgram.TagsRecipe', to='foodgram.tag', verbose_name='Recipe tags'),
        ),
        migrations.AddField(
            model_name='purchasinglist',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='purchasing_list', to='foodgram.recipe', verbose_name='purchasing recipe'),
        ),
        migrations.AddField(
            model_name='purchasinglist',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='purchasing_list', to=settings.AUTH_USER_MODEL, verbose_name='purchasing user'),
        ),
        migrations.AddField(
            model_name='ingredientsrecipe',
            name='ingredient',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ingredients_list', to='foodgram.ingredient', verbose_name='description'),
        ),
        migrations.AddField(
            model_name='ingredientsrecipe',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ingredients_list', to='foodgram.recipe', verbose_name='Recipe'),
        ),
        migrations.AddField(
            model_name='favoriterecipe',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorite', to='foodgram.recipe', verbose_name='favorite recipe'),
        ),
        migrations.AddField(
            model_name='favoriterecipe',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorite', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddConstraint(
            model_name='tagsrecipe',
            constraint=models.UniqueConstraint(fields=('recipe', 'tag'), name='unique_tags_for_recipe'),
        ),
        migrations.AddConstraint(
            model_name='purchasinglist',
            constraint=models.UniqueConstraint(fields=('recipe', 'user'), name='unique_shopping_pair'),
        ),
        migrations.AddConstraint(
            model_name='ingredientsrecipe',
            constraint=models.UniqueConstraint(fields=('ingredient', 'recipe'), name='unique_ingredients_for_recipe'),
        ),
        migrations.AddConstraint(
            model_name='favoriterecipe',
            constraint=models.UniqueConstraint(fields=('recipe', 'user'), name='unique_favorite_recipes'),
        ),
    ]
