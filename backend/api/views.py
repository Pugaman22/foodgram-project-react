from http import HTTPStatus
from typing import Any

from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.db.models import Exists, OuterRef, Value
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from foodgram.models import (Favorite, Ingredient, IngredientsRecipe,
                             PurchasingList, Recipe, Tag)
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from users.models import Follow

from .fav_cart_base_view_set import FavoriteCartBaseViewSet
from .filters import RecipeFilter
from .pagination import PageLimitPagination
from .permissions import IsAuthorOrReadOnly
from .serializers import (FavoriteSerializer, FollowSerializer,
                          IngredientSerializer, PurchasingListSerializer,
                          RecipeGetSerializer, RecipePostSerializer,
                          TagSerializer)

User = get_user_model()


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthorOrReadOnly,)
    filterset_class = RecipeFilter
    pagination_class = PageLimitPagination

    def get_queryset(self):
        if self.request.user.is_authenticated:
            favorited = Favorite.objects.filter(
                    user=self.request.user,
                    recipe=OuterRef('pk')
                )
            in_cart = PurchasingList.objects.filter(
                    user=self.request.user,
                    recipe=OuterRef('pk')
                )
            queryset = Recipe.objects.all().select_related(
                'author').prefetch_related('tags').annotate(
                is_favorited=Exists(favorited)).annotate(
                    is_in_shopping_cart=Exists(in_cart))

        else:
            print("not authenticated")
            queryset = Recipe.objects.all().select_related(
                'author').prefetch_related('tags').annotate(
                    is_favorited=Value(False)).annotate(
                        is_in_shopping_cart=Value(False))
        return queryset

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
        return Follow.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        author = get_object_or_404(
            User,
            id=self.kwargs.get('author_id')
        )
        if author == request.user:
            return Response(
                'You cannot subscribe on yourself',
                status=HTTPStatus.BAD_REQUEST
            )
        try:
            Follow.objects.get_or_create(author=author, user=self.request.user)
        except IntegrityError:
            return Response(
                'You have been already subscribed on this author.',
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


class FavoriteViewSet(FavoriteCartBaseViewSet):
    serializer_class = FavoriteSerializer
    permission_classes = (IsAuthenticated,)

    def __init__(self,  **kwargs: Any) -> None:
        super().__init__(Favorite, **kwargs)


class PurchasingListViewSet(FavoriteCartBaseViewSet):
    serializer_class = PurchasingListSerializer
    permission_classes = (IsAuthenticated,)

    def __init__(self,  **kwargs: Any) -> None:
        super().__init__(PurchasingList, **kwargs)


class ShoppingCartViewSet(APIView):
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
