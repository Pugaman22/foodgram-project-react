# Generated by Django 4.2.4 on 2023-09-07 18:48

import colorfield.fields
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='FavoriteRecipe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'verbose_name': 'Favorite recipe',
                'verbose_name_plural': 'Favorite recipes',
                'ordering': ['-recipe'],
            },
        ),
        migrations.CreateModel(
            name='Ingredient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='ingredient name')),
                ('units', models.CharField(max_length=20, verbose_name='unit of measurement')),
            ],
            options={
                'verbose_name_plural': 'Ingredients',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='IngredientsRecipe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.SmallIntegerField(validators=[django.core.validators.MinValueValidator(1, message='Minimaum value is 1!')], verbose_name='Ingredient quantity')),
            ],
            options={
                'verbose_name': 'List of ingredients for recipe',
                'verbose_name_plural': 'List of ingredients for recipes',
            },
        ),
        migrations.CreateModel(
            name='PurchasingList',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'verbose_name': 'Recipe for purchasing',
                'verbose_name_plural': 'Recipes for purchasing',
                'ordering': ('recipe',),
            },
        ),
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='recipe name')),
                ('description', models.TextField(help_text='Write a description', verbose_name='recipe description')),
                ('image', models.ImageField(upload_to='foodgram/images/', verbose_name='meal picture')),
                ('cooking_time', models.SmallIntegerField(help_text='Type cooking time using minutes.', validators=[django.core.validators.MinValueValidator(1, message='Minimum value is 1!'), django.core.validators.MaxValueValidator(1440, message='Maximum value is 1440 (24h)!')])),
                ('pub_date', models.DateTimeField(auto_now_add=True, verbose_name='Publication date')),
            ],
            options={
                'verbose_name_plural': 'Recipes',
                'ordering': ['-pub_date'],
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True, verbose_name='tag name')),
                ('colour', colorfield.fields.ColorField(default='#FFFFFF', image_field=None, max_length=18, samples=None, unique=True, verbose_name='tag colour')),
                ('slug', models.SlugField(unique=True, verbose_name='tag slug')),
            ],
            options={
                'verbose_name_plural': 'Tags',
            },
        ),
        migrations.CreateModel(
            name='TagsRecipe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('recipe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tags_list', to='foodgram.recipe', verbose_name='recipe')),
                ('tag', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tags_list', to='foodgram.tag', verbose_name='tag')),
            ],
            options={
                'verbose_name': 'List of tags for recipe',
                'verbose_name_plural': 'List of tags for recipes',
            },
        ),
    ]
