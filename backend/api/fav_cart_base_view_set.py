from http import HTTPStatus

from django.shortcuts import get_object_or_404
from recipes.models import Recipe
from rest_framework import mixins, viewsets
from rest_framework.response import Response

from .serializers import RecipeSerializer


class CreateDestroyViewSet(mixins.CreateModelMixin,
                           mixins.DestroyModelMixin,
                           viewsets.GenericViewSet):
    pass


class RelationBaseViewSet(CreateDestroyViewSet):
    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        recipe = get_object_or_404(
            Recipe,
            id=self.kwargs.get('recipe_id')
        )
        o, created = self.model.objects.get_or_create(
            user=self.request.user,
            recipe=recipe)
        if not created:
            return Response(
                'This recipe has already been added.',
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
