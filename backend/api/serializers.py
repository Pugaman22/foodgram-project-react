from rest_framework import serializers
from foodgram.models import (Favorite, Recipe, Ingredient, Tag,
                             IngredientsRecipe, PurchasingList, TagsRecipe)
from users.models import Follow
from django.contrib.auth import get_user_model

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
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


class Base64ImageField(serializers.ImageField):

    def to_internal_value(self, data):
        import base64
        import uuid

        import six
        from django.core.files.base import ContentFile

        if isinstance(data, six.string_types):
            if 'data:' in data and ';base64,' in data:
                header, data = data.split(';base64,')

            try:
                decoded_file = base64.b64decode(data)
            except TypeError:
                self.fail('invalid_image')

            file_name = str(uuid.uuid4())[:12]
            file_extension = self.get_file_extension(file_name, decoded_file)
            complete_file_name = "%s.%s" % (file_name, file_extension, )
            data = ContentFile(decoded_file, name=complete_file_name)

        return super(Base64ImageField, self).to_internal_value(data)

    def get_file_extension(self, file_name, decoded_file):
        import imghdr

        extension = imghdr.what(file_name, decoded_file)
        extension = "jpg" if extension == "jpeg" else extension

        return extension


class TagSerializer(serializers.ModelSerializer):
    '''Serializer for Tag model.'''
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    '''Serializer for Ingredient model.'''
    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientsRecipeSerializer(serializers.ModelSerializer):
    '''Serializer for IngredientsRecipe model.'''
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    units = serializers.ReadOnlyField(source='ingredient.units')

    class Meta:
        model = IngredientsRecipe
        fields = ('id', 'name', 'units', 'quantity')


class IngredientRecipeSmallSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')
    # # amount = serializers.IntegerField(source='quantity')
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientsRecipe
        fields = ('id', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    '''Serializer for Recipe model.'''

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time', 'tags')


class RecipeGetSerializer(serializers.ModelSerializer):
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField(
    )
    tags = TagSerializer(many=True)
    author = UserSerializer(many=False)
    ingredients = IngredientsRecipeSerializer(
        many=True,
        # source='ingredientrecipes'
    )

    class Meta:
        model = Recipe
        fields = '__all__'

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return (
            request.user.is_authenticated
            and Favorite.objects.filter(
                user=request.user,
                recipe__id=obj.id
            ).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return (
            request.user.is_authenticated
            and PurchasingList.objects.filter(
                user=request.user,
                recipe__id=obj.id
            ).exists()
        )


class RecipePostSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    image = Base64ImageField(
        max_length=None,
        use_url=False
    )
    ingredients = IngredientRecipeSmallSerializer(
        # source='ingredientrecipes',
        many=True
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    text = serializers.CharField(source="description")

    class Meta:
        model = Recipe
        # fields = '__all__'
        exclude = ('description',)

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return (
            request.user.is_authenticated
            and Favorite.objects.filter(
                user=request.user,
                recipe__id=obj.id
            ).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return (
            request.user.is_authenticated
            and PurchasingList.objects.filter(
                user=request.user,
                recipe__id=obj.id
            ).exists()
        )

    def validate_ingredients(self, value):
        ingredients_list = []
        ingredients = value
        for ingredient in ingredients:
            # print(ingredient)
            if ingredient['amount'] < 1:
                raise serializers.ValidationError(
                    'Убедитесь, что количество больше 0')
            check_id = ingredient["ingredient"]['id']
            check_ingredient = Ingredient.objects.filter(id=check_id)
            if not check_ingredient.exists():
                raise serializers.ValidationError(
                    'Ингредиент отсутствует')
            if check_ingredient in ingredients_list:
                raise serializers.ValidationError(
                    'Ингредиент повторяется')
            ingredients_list.append(check_ingredient)
        return value

    def add_tags_and_ingredients(self, tags, ingredients, recipe):
        for tag in tags:
            recipe.tags.add(tag)
            recipe.save()
        for ingredient in ingredients:

            if not IngredientsRecipe.objects.filter(
                    ingredient_id=ingredient['ingredient']['id'],
                    recipe=recipe).exists():
                ingredient_recipe = IngredientsRecipe.objects.create(
                    ingredient_id=ingredient['ingredient']['id'],
                    amount=ingredient['amount'],
                    recipe=recipe
                )
                ingredient_recipe.save()
            else:
                IngredientsRecipe.objects.filter(
                    recipe=recipe
                ).delete()
                recipe.delete()
                raise serializers.ValidationError(
                    'Ингредиент уже есть в рецепте'
                )
        # recipe.save()
        return recipe

    def create(self, validated_data):
        author = validated_data.get('author')
        name = validated_data.get('name')
        image = validated_data.get('image')
        description = validated_data.get('description')
        # ingredients = validated_data.pop('ingredientrecipes')
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        cooking_time = validated_data.get('cooking_time')
        recipe = Recipe.objects.create(
            author=author,
            name=name,
            image=image,
            description=description,
            cooking_time=cooking_time,
        )
        recipe = self.add_tags_and_ingredients(tags, ingredients, recipe)
        print("1" * 30)
        print(recipe.ingredients)
        return recipe

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


class FollowSerializer(serializers.ModelSerializer):
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
