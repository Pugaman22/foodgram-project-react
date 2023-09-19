from django.contrib import admin

from foodgram.models import (Favorite, Ingredient, IngredientsRecipe,
                             PurchasingList, Recipe, Tag, TagsRecipe)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'colour', 'slug',)
    search_fields = ('name',)
    list_filter = ('name',)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit',)
    search_fields = ('name',)
    list_filter = ('name',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'author', 'pub_date', 'image', 'description')
    search_fields = ('name', 'author',)
    list_filter = ('name', 'author',)


@admin.register(IngredientsRecipe)
class IngredientsRecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipe', 'ingredient', 'amount',)
    list_filter = ('recipe', 'ingredient')


@admin.register(TagsRecipe)
class TagsRecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipe', 'tag',)
    list_filter = ('recipe', 'tag')


@admin.register(Favorite)
class FavoriteRecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipe', 'user',)
    list_filter = ('recipe', 'user',)
    search_fields = ('user',)


@admin.register(PurchasingList)
class PurchasingListAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipe', 'user',)
    list_filter = ('recipe', 'user',)
    search_fields = ('user',)
