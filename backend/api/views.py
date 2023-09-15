from http import HTTPStatus
from django.db import IntegrityError
from django.http import HttpResponse

from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from .serializers import (FavoriteSerializer, FollowSerializer,
                          PurchasingListSerializer, RecipeGetSerializer,
                          RecipePostSerializer, RecipeSerializer,
                          TagSerializer, IngredientSerializer)
from .permissions import IsAuthenticated, IsAuthorOrReadOnly
from .filters import RecipeFilter
from foodgram.models import (Favorite, IngredientsRecipe, PurchasingList, Tag,
                             Ingredient, Recipe)
from users.models import Follow
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework import mixins, viewsets
from rest_framework.views import APIView

User = get_user_model()


class CreateDestroyViewSet(mixins.CreateModelMixin,
                           mixins.DestroyModelMixin,
                           viewsets.GenericViewSet):
    pass


class PageLimitPagination(PageNumberPagination):
    page_size = 6
    page_size_query_param = 'limit'


class RecipesLimitPagination(PageNumberPagination):
    page_size_query_param = 'recipes_limit'


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filter_class = RecipeFilter
    pagination_class = PageLimitPagination

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeGetSerializer
        return RecipePostSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class FollowViewSet(viewsets.ModelViewSet):
    serializer_class = FollowSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = PageLimitPagination

    def get_queryset(self):
        # return Follow.objects.filter(following__user=self.request.user)
        return Follow.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        author = get_object_or_404(
            User,
            id=self.kwargs.get('author_id')
        )
        if author == request.user:
            return Response(
                'Нельзя подписываться на себя',
                status=HTTPStatus.BAD_REQUEST
            )
        try:
            Follow.objects.create(author=author, user=self.request.user)
        except IntegrityError:
            return Response(
                'Вы уже подписаны на данного автора',
                status=HTTPStatus.BAD_REQUEST
            )
        follow = get_object_or_404(
            Follow,
            author=author,
            user=request.user
        )
        serializer = FollowSerializer(follow, many=False)
        return Response(
            data=serializer.data,
            status=HTTPStatus.CREATED
        )

    def delete(self, request, *args, **kwargs):
        author = get_object_or_404(
            User,
            id=self.kwargs.get('author_id')
        )
        get_object_or_404(
            Follow,
            author=author,
            user=request.user
        ).delete()
        return Response(status=HTTPStatus.NO_CONTENT)


class FavoriteViewSet(CreateDestroyViewSet):
    serializer_class = FavoriteSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        recipe = get_object_or_404(
            Recipe,
            id=self.kwargs.get('recipe_id')
        )
        Favorite.objects.create(
            user=request.user,
            recipe=recipe
        )
        serializer = RecipeSerializer(
            recipe,
            many=False
        )
        return Response(
            data=serializer.data,
            status=HTTPStatus.CREATED
        )

    def delete(self, request, *args, **kwargs):
        recipe = get_object_or_404(
            Recipe,
            id=self.kwargs.get('recipe_id')
        )
        get_object_or_404(
            Favorite,
            user=request.user,
            recipe=recipe
        ).delete()
        return Response(status=HTTPStatus.NO_CONTENT)


class PurchasingListViewSet(viewsets.ModelViewSet):
    serializer_class = PurchasingListSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return PurchasingList.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        recipe = get_object_or_404(
            Recipe,
            id=self.kwargs.get('recipe_id')
        )
        try:
            PurchasingList.objects.create(user=self.request.user,
                                          recipe=recipe)
        except IntegrityError:
            return Response(
                'Этот рецепт уже в списке покупок',
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
            PurchasingList,
            user=request.user,
            recipe=recipe
        ).delete()
        return Response(status=HTTPStatus.NO_CONTENT)


class ShoppingListViewSet(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = request.user
        carts = PurchasingList.objects.filter(user=user)
        recipes = [cart.recipe for cart in carts]
        cart = {}
        for recipe in recipes:
            for ingredient in recipe.ingredients.all():
                amount = get_object_or_404(
                    IngredientsRecipe,
                    recipe=recipe,
                    ingredient=ingredient
                ).amount
                if ingredient.name not in cart:
                    cart[ingredient.name] = amount
                else:
                    cart[ingredient.name] += amount
        content = ''
        for item in cart:
            units = get_object_or_404(
                Ingredient,
                name=item
            ).measurement_unit
            content += f'{item}: {cart[item]}{units}\n'
        response = HttpResponse(
            content, content_type='text/plain,charset=utf8'
        )
        response['Content-Disposition'] = 'attachment; filename="cart.txt"'
        return response
