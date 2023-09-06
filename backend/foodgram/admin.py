from django.contrib import admin
from foodgram.models import (Ingredient, Recipe, Tag, IngredientsRecipe,
                             TagsRecipe, FavoriteRecipe, PurchasingList)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'colour', 'slug',)
    search_fields = ('name',)
    list_filter = ('name',)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'units',)
    search_fields = ('name',)
    list_filter = ('name',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'author', 'pub_date', 'image', 'description')
    search_fields = ('name', 'author',)
    list_filter = ('name', 'author',)


@admin.register(IngredientsRecipe)
class IngredientsRecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipe', 'ingredient', 'quantity',)
    list_filter = ('recipe', 'ingredient')


@admin.register(TagsRecipe)
class TagsRecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipe', 'tag',)
    list_filter = ('recipe', 'tag')


@admin.register(FavoriteRecipe)
class FavoriteRecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipe', 'user',)
    list_filter = ('recipe', 'user',)
    search_fields = ('user',)


@admin.register(PurchasingList)
class PurchasingListAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipe', 'user',)
    list_filter = ('recipe', 'user',)
    search_fields = ('user',)
