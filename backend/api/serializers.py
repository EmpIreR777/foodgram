from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from drf_extra_fields.fields import Base64ImageField

from users.models import User, Follow
from recipes.models import (
    Recipe,
    Tag,
    RecipeIngredient,
    Ingredient,
    FavoriteRecipe,
    ShoppingCart,
)


class AvatarSerializer(serializers.ModelSerializer):
    """Серилизатор аватарки."""

    avatar = Base64ImageField()

    class Meta:
        model = User
        fields = ('avatar',)


class UserSerializer(serializers.ModelSerializer):
    """Серилизатор Юзера."""

    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'avatar',
        )

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Follow.objects.filter(user=user, following=obj).exists()


class TagSerializer(serializers.ModelSerializer):
    """Серилизатор тэгов."""

    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'slug'
        )


class IngredientSerializer(serializers.ModelSerializer):
    """Серилизатор ингредиентов."""

    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit',
        )


class IngredientCreateUpdateSerializer(serializers.ModelSerializer):
    """Серилизатор добавления ингредиентов."""

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(), required=True)
    amount = serializers.IntegerField(min_value=1)

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Серилизатор количества ингредиентов."""

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeReadSerializer(serializers.ModelSerializer):
    """Серилизатор рецептов."""

    tags = TagSerializer(many=True)
    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(
        many=True, source='recipe_ingredient_set')
    is_favorited = serializers.SerializerMethodField(
        read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(
        read_only=True)
    image = Base64ImageField(required=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.favorite_recipes.filter(recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.shopping_carts.filter(recipe=obj).exists()


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    """Серилизатор добавления рецептов."""

    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all())
    author = UserSerializer(read_only=True)
    ingredients = IngredientCreateUpdateSerializer(
        many=True,
    )
    image = Base64ImageField(required=True)

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'name', 'image', 'text', 'cooking_time')
        read_only_fields = ('author',)

    def validate(self, attrs):
        tags = attrs.get('tags')
        ingredients = attrs.get('ingredients')
        if not ingredients:
            raise serializers.ValidationError(
                {'ingredients': 'Поле отсутствует'})
        if not tags:
            raise serializers.ValidationError(
                {'tags': 'Поле отсутствует'})
        if len(tags) != len(set(tags)):
            raise serializers.ValidationError(
                {'tags:': 'Теги не уникальны'})
        double_ingredient = {item['id'] for item in ingredients}
        if len(double_ingredient) != len(ingredients):
            raise serializers.ValidationError(
                {'ingredients': 'Дублирование ингредиентов'})
        return attrs

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(
            author=self.context['request'].user, **validated_data)
        recipe.tags.set(tags)
        RecipeIngredient.objects.bulk_create(
            RecipeIngredient(recipe=recipe,
                             ingredient=ingredient['id'],
                             amount=ingredient['amount'])
            for ingredient in ingredients
        )
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags', None)
        if tags is not None:
            instance.tags.set(tags)
        ingredients = validated_data.pop('ingredients', None)
        if ingredients is not None:
            instance.ingredients.clear()
            RecipeIngredient.objects.bulk_create(
                RecipeIngredient(recipe=instance,
                                 ingredient=ingredient['id'],
                                 amount=ingredient['amount'])
                for ingredient in ingredients
            )
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return RecipeReadSerializer(instance, context=self.context).data


class RecipeShopFavorSerializer(serializers.ModelSerializer):
    """Серилизатор добавления изображения рецепта."""

    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = fields


class SubscriptionsSerializer(UserSerializer):
    """Серилизатор подписок друг на друга."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
            'avatar',
        )

    def get_recipes(self, obj):
        recipes = obj.recipes.all()
        recipes_limit = self.context[
            'request'].query_params.get('recipes_limit')
        if recipes_limit and recipes_limit.isdigit():
            recipes = recipes[:int(recipes_limit)]
        return RecipeShopFavorSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class SubscribeSerializer(serializers.ModelSerializer):
    """Сериализатор подписок список."""

    class Meta:
        model = Follow
        fields = ('user', 'following')
        validators = [
            UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=['user', 'following'],
                message='Вы уже подписаны на этого автора!',
            )
        ]

    def validate(self, attrs):
        user = attrs['user']
        following = attrs['following']
        if user == following:
            raise serializers.ValidationError(
                {'error': 'Нельзя подписаться на себя.'})
        return attrs

    def to_representation(self, instance):
        return SubscriptionsSerializer(
            instance.following, context=self.context).data


class BaseRecipeSerializer(serializers.ModelSerializer):
    """Серилизатор базовый для избраного и корзины."""

    class Meta:
        abstract = True
        model = None
        fields = ('user', 'recipe')

    def to_representation(self, instance):
        return RecipeShopFavorSerializer(instance.recipe,
                                         context=self.context).data


class ShoppingCartSerializer(BaseRecipeSerializer):
    """Сериализатор корзины."""

    class Meta(BaseRecipeSerializer.Meta):
        model = ShoppingCart
        validators = [
            UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(),
                fields=['user', 'recipe'],
                message='Вы уже добавили рецепт в корзину!',
            )
        ]


class FavoriteRecipeSerializer(BaseRecipeSerializer):
    """Сериализатор избранных рецептов."""

    class Meta(BaseRecipeSerializer.Meta):
        model = FavoriteRecipe
        validators = [
            UniqueTogetherValidator(
                queryset=FavoriteRecipe.objects.all(),
                fields=['user', 'recipe'],
                message='Вы уже подписаны на этого автора!',
            )
        ]
