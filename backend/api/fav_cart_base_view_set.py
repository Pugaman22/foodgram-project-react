
from http import HTTPStatus
from typing import Any

from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from foodgram.models import Recipe
from rest_framework import mixins, viewsets
from rest_framework.response import Response

from .serializers import RecipeSerializer


class CreateDestroyViewSet(mixins.CreateModelMixin,
                           mixins.DestroyModelMixin,
                           viewsets.GenericViewSet):
    pass


class FavoriteCartBaseViewSet(CreateDestroyViewSet):

    def __init__(self, model, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.model = model

    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        recipe = get_object_or_404(
            Recipe,
            id=self.kwargs.get('recipe_id')
        )
        try:
            self.model.objects.create(user=self.request.user,
                                      recipe=recipe)
        except IntegrityError:
            return Response(
                'Этот рецепт уже добавлен',
                status=HTTPStatus.BAD_REQUEST
            )
        serializer = RecipeSerializer(recipe, many=False)
        return Response(data=serializer.data, status=HTTPStatus.CREATED)

    def delete(self, request, *args, **kwargs):
        recipe = get_object_or_404(
            Recipe,
            id=self.kwargs.get('recipe_id')
        )
        get_object_or_404(
            self.model,
            user=request.user,
            recipe=recipe
        ).delete()
        return Response(status=HTTPStatus.NO_CONTENT)
