from django.shortcuts import render
from rest_framework import viewsets
from api.serializers import TagSerializer, IngredientSerializer
from foodgram.models import Tag, Ingredient


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    # pagination_class = None
