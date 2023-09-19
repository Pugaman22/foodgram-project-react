from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (FavoriteViewSet, FollowViewSet, IngredientViewSet,
                       PurchasingListViewSet, RecipeViewSet,
                       ShoppingCartViewSet, TagViewSet)

router = DefaultRouter()

router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('tags', TagViewSet, basename='tags')
router.register('recipes', RecipeViewSet, basename='recipes')


urlpatterns = [

    path(
        'recipes/<int:recipe_id>/favorite/',
        FavoriteViewSet.as_view({'post': 'create', 'delete': 'delete'}),
        name='favorites'
    ),
    path(
        'recipes/<int:recipe_id>/shopping_cart/',
        PurchasingListViewSet.as_view({'post': 'create', 'delete': 'delete'}),
        name='shopping_cart'
    ),
    path(
        'recipes/download_shopping_cart/',
        ShoppingCartViewSet.as_view(),
        name='download'
    ),
    path(
        'users/subscriptions/',
        FollowViewSet.as_view({'get': 'list'}),
        name='subscriptions'
    ),

    path('', include('djoser.urls')),
    path(
        'users/<int:author_id>/subscribe/',
        FollowViewSet.as_view({'post': 'create', 'delete': 'delete'}),
        name='to_subscribe'
    ),
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
