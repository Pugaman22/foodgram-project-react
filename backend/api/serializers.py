from django.contrib.auth import get_user_model
from django.db import transaction
from django.shortcuts import get_object_or_404
from djoser.serializers import UserSerializer
from drf_extra_fields.fields import Base64ImageField
from recipes.models import (Favorite, Ingredient, IngredientsRecipe,
                            PurchasingList, Recipe, Tag, TagsRecipe)
from rest_framework import serializers
from users.models import Follow

User = get_user_model()


class UserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'first_name',
            'last_name', 'is_subscribed', 'password'
        )
        extra_kwargs = {'password': {'write_only': True}}

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return (
            request.user.is_authenticated
            and Follow.objects.filter(
                user=request.user,
                author__id=obj.id
            ).exists()
        )


class TagSerializer(serializers.ModelSerializer):
    """Serializer for Tag model."""
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    """Serializer for Ingredient model."""
    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientRecipeSmallSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')

    class Meta:
        model = IngredientsRecipe
        fields = ('id', 'amount')


class IngredientsRecipeSerializer(serializers.ModelSerializer):
    """Serializer for IngredientsRecipe model."""
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    units = serializers.ReadOnlyField(source='ingredient.units')

    class Meta:
        model = IngredientsRecipe
        fields = ('id', 'name', 'units', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for Recipe model."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time', 'tags')


class RecipeGetSerializer(serializers.ModelSerializer):
    is_favorited = serializers.BooleanField(read_only=True, default=False)
    is_in_shopping_cart = serializers.BooleanField(
        read_only=True,
        default=False)
    tags = TagSerializer(many=True)
    author = UserSerializer()
    ingredients = IngredientsRecipeSerializer(
        source='ingredients_list', many=True)

    class Meta:
        model = Recipe
        fields = '__all__'


class RecipePostSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    image = Base64ImageField(
        required=True,
        max_length=None,
        use_url=False
    )
    ingredients = IngredientRecipeSmallSerializer(
        source='ingredients_list',
        many=True
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    text = serializers.CharField(source="description")

    class Meta:
        model = Recipe
        exclude = ('description',)

    def validate_ingredients(self, ingredients):
        ids = [i['ingredient']['id'] for i in ingredients]
        ingredients_set = set(ids)
        if len(ids) != len(ingredients_set):
            raise serializers.ValidationError('Ингредиент повторяется')
        if Ingredient.objects.filter(id__in=ids).count() != len(ids):
            raise serializers.ValidationError('Ингредиент отсутствует')

        for ingredient in ingredients:
            if ingredient['amount'] < 1:
                raise serializers.ValidationError(
                    'Убедитесь, что количество больше 0')
        return ingredients

    def add_tags_and_ingredients(self, tags, ingredients, recipe):
        recipe.tags.set(tags)

        IngredientsRecipe.objects.bulk_create(
            IngredientsRecipe(
                recipe=recipe,
                ingredient=get_object_or_404(
                    Ingredient, id=ingredient['ingredient']['id']
                ),
                amount=ingredient['amount']
            )
            for ingredient in ingredients)

        return recipe

    @transaction.atomic
    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients_list')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe = self.add_tags_and_ingredients(tags, ingredients, recipe)

        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        TagsRecipe.objects.filter(recipe=instance).delete()
        IngredientsRecipe.objects.filter(recipe=instance).delete()
        instance = self.add_tags_and_ingredients(
            tags, ingredients, instance
        )
        super().update(instance, validated_data)
        instance.save()
        return instance

class FollowCreateSerializer(serializers.ModelSerializer):
    def validate_author_id(self, author_id):
        # этот метод не вызывается
        # не смог разобраться, почему 
        print("validate_author_id", author_id)
        return author_id
    
    def validate(self, data):
        print("validate", data.keys())
        author_id = self.context["author_id"] 
        request = self.context["request"]
        if author_id == request.user.id:
            raise serializers.ValidationError(
                'You cannot subscribe on yourself'
            )
        return data

    class Meta:
        model = Follow
        fields=('author_id',)

class FollowCreateSerializer(serializers.ModelSerializer):
    def validate_author_id(self, author_id):
        print("validate_author_id", author_id)
        return author_id

    def validate(self, data):
        print("validate", data.keys())
        author_id = self.context["author_id"]
        request = self.context["request"]
        if author_id == request.user.id:
            raise serializers.ValidationError(
                'You cannot subscribe on yourself'
            )
        return data

    class Meta:
        model = Follow
        fields = ('author_id',)


class FollowSerializer(serializers.ModelSerializer):
    """Serializer for Follow model."""
    is_subscribed = serializers.SerializerMethodField()
    email = serializers.ReadOnlyField(source='author.email')
    id = serializers.ReadOnlyField(source='author.id')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(
        source='author.recipes.count',
        read_only=True
    ) 
    def validate_id(self, id):
        print("validate_id")

    def validate(self, data):
        print("validate")
        author = get_object_or_404(
            User,
            id=id
        )
        if author == self.request.user:
            raise serializers.ValidationError('You cannot subscribe on yourself')
        return data
    
    def create(self, validated_data):
        print("cr")
        print(validated_data)
        author_id = validated_data.pop('author_id')
        # tags = validated_data.pop('tags')
        # recipe = Recipe.objects.create(**validated_data)
        # recipe = self.add_tags_and_ingredients(tags, ingredients, recipe)

        # return recipe

    def validate_id(self, id):
        print("validate_id")

    def validate(self, data):
        print("validate")
        author = get_object_or_404(
            User,
            id=id
        )
        if author == self.request.user:
            raise serializers.ValidationError(
                'You cannot subscribe on yourself')
        return data

    class Meta:
        model = Follow
        fields = (
            'id', 'username', 'email', 'first_name',
            'last_name', 'is_subscribed', 'recipes',
            'recipes_count'
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if not request:
            return True
        return (
            Follow.objects.filter(
                user=request.user,
                author__id=obj.id
            ).exists()
            and request.user.is_authenticated
        )

    def get_recipes(self, obj):
        try:
            recipes_limit = int(
                self.context.get('request').query_params['recipes_limit']
            )
            recipes = Recipe.objects.filter(author=obj.author)[:recipes_limit]
        except Exception:
            recipes = Recipe.objects.filter(author=obj.author)
        serializer = RecipeSerializer(recipes, many=True)
        return serializer.data


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = '__all__'


class PurchasingListSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchasingList
        fields = '__all__'
