from rest_framework import serializers
from foodgram.models import Recipe, Ingredient, Tag, IngredientsRecipe
from users.models import Subscription
from django.contrib.auth import get_user_model

User = get_user_model()


class TagSerializer(serializers.ModelSerializer):
    '''Serializer for Tag model.'''
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    '''Serializer for Ingredient model.'''
    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientsRecipeSerializer(serializers.ModelSerializer):
    '''Serializer for IngredientsRecipe model.'''
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    units = serializers.ReadOnlyField(source='ingredient.units')

    class Meta:
        model = IngredientsRecipe
        fields = ('id', 'name', 'units', 'quantity')


class RecipeSerializer(serializers.ModelSerializer):
    '''Serializer for Recipe model.'''

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time', 'tags')


class SubscriptionSerializer(serializers.ModelSerializer):
    '''Serializer for Subscription model.'''

    email = serializers.ReadOnlyField(source='author.email')
    id = serializers.ReadOnlyField(source='author.id')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.BooleanField(read_only=True)
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.ReadOnlyField(source='author.recipes.count')

    class Meta:
        model = Subscription
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )
