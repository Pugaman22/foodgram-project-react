from rest_framework import serializers
from foodgram.models import Recipe, Ingredient


class RecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
