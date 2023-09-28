from django_filters.rest_framework import FilterSet, filters
from recipes.models import PurchasingList, Recipe, Ingredient


class IngredientFilter(FilterSet):
    name = filters.CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(FilterSet):
    author = filters.CharFilter(
        field_name='author__id',
    )
    tags = filters.AllValuesMultipleFilter(
        field_name='tags__slug',
    )
    is_favorited = filters.BooleanFilter(
        method='get_is_favorited'
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='get_is_in_shopping_cart'
    )

    def get_is_favorited(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(pk=value)

    def get_is_in_shopping_cart(self, queryset, name, value):
        if not value:
            return queryset
        carts = PurchasingList.objects.all()
        return queryset.filter(
            pk__in=(cart.recipe.pk for cart in carts)
        )

    class Meta:
        model = Recipe
        fields = (
            'author', 'tags', 'is_favorited', 'is_in_shopping_cart'
        )
