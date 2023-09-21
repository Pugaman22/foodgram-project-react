from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from recipes.models import Ingredient, IngredientsRecipe, PurchasingList

User = get_user_model()


def get_shopping_list(user: User):

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
    return content
