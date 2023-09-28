from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from recipes.models import Favorite, Ingredient, PurchasingList, Recipe, Tag
from rest_framework import viewsets, status
from rest_framework.generics import ListAPIView
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import Follow

from .fav_cart_base_view_set import RelationBaseViewSet
from .filters import RecipeFilter, IngredientFilter
from .pagination import PageLimitPagination
from .permissions import IsAuthorOrReadOnly
from .serializers import (FavoriteSerializer, 
                          IngredientSerializer,SubscribeListSerializer,SubscribeSerializer,
                          PurchasingListSerializer, RecipeGetSerializer,
                          RecipePostSerializer, TagSerializer)
from .services import get_shopping_list

User = get_user_model()


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    # permission_classes = (AllowAny,)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filterset_class = IngredientFilter
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthorOrReadOnly,)
    filterset_class = RecipeFilter
    pagination_class = PageLimitPagination

    def get_queryset(self):
        if self.request.method == 'GET':
            return Recipe.objects.fill_favs_and_in_cart(
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



class FavoriteViewSet(RelationBaseViewSet):
    model = Favorite
    serializer_class = FavoriteSerializer
    permission_classes = (IsAuthenticated,)


class PurchasingListViewSet(RelationBaseViewSet):
    model = PurchasingList
    serializer_class = PurchasingListSerializer
    permission_classes = (IsAuthenticated,)




class SubscribeListView(ListAPIView):
    """Список покупок"""
    serializer_class = SubscribeListSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Follow.objects.filter(user=self.request.user)
    


class MainSubscribeViewSet(APIView):
    """Подписаться/отписаться на автора рецепта"""
    serializer_class = SubscribeSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = PageLimitPagination
    # pagination_class = CustomPagination

    def post(self, request, *args, **kwargs):
        user_id = self.kwargs.get('user_id')
        if user_id == request.user.id:
            return Response(
                {'error': 'Нельзя подписаться на себя'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if Follow.objects.filter(
                user=request.user,
                author_id=user_id
        ).exists():
            return Response(
                {'error': 'Вы уже подписаны на пользователя'},
                status=status.HTTP_400_BAD_REQUEST
            )
        author = get_object_or_404(User, id=user_id)
        Follow.objects.create(
            user=request.user,
            author_id=user_id
        )
        return Response(
            self.serializer_class(author, context={'request': request}).data,
            status=status.HTTP_201_CREATED
        )

    def delete(self, request, *args, **kwargs):
        user_id = self.kwargs.get('user_id')
        get_object_or_404(User, id=user_id)
        subscription = Follow.objects.filter(
            user=request.user,
            author_id=user_id
        )
        if subscription:
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'error': 'Вы не подписаны на пользователя'},
            status=status.HTTP_400_BAD_REQUEST
        )