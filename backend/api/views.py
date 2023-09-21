from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from recipes.models import Favorite, Ingredient, PurchasingList, Recipe, Tag
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from users.models import Follow

from .fav_cart_base_view_set import RelationBaseViewSet
from .filters import RecipeFilter
from .pagination import PageLimitPagination
from .permissions import IsAuthorOrReadOnly
from .serializers import (FavoriteSerializer, FollowSerializer,
                          IngredientSerializer, PurchasingListSerializer,
                          RecipeGetSerializer, RecipePostSerializer,
                          TagSerializer)
from .services import get_shopping_list

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
        if self.request.method == 'GET':
            return Recipe.objects_with_related_fields.fill_favs_and_in_cart(
                self.request.user)

        return Recipe.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeGetSerializer
        return RecipePostSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(methods=["get"], detail=False)
    def download_shopping_cart(self, request):
        return FileResponse(
            get_shopping_list(request.user),
            content_type='text/plain,charset=utf8',
            as_attachment=True, filename="cart.txt"
        )


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


class FavoriteViewSet(RelationBaseViewSet):
    model = Favorite
    serializer_class = FavoriteSerializer
    permission_classes = (IsAuthenticated,)


class PurchasingListViewSet(RelationBaseViewSet):
    model = PurchasingList
    serializer_class = PurchasingListSerializer
    permission_classes = (IsAuthenticated,)
