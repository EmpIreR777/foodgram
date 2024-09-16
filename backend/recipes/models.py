from django.db import models
from django.core.validators import MinValueValidator
from django.utils.crypto import get_random_string

from users.models import User


class Recipe(models.Model):
    """Модель рецепта."""

    ingredients = models.ManyToManyField(
        'Ingredient', related_name='recipes',
        through='RecipeIngredient',
        verbose_name='Ингредиент'
    )
    tags = models.ManyToManyField(
        'Tag', related_name='recipes',
        verbose_name='Тэг'
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор'
    )
    image = models.ImageField(
        'Изображение рецепта',
        upload_to='media/recipes'
    )
    name = models.CharField(
        'Название рецепта',
        max_length=256
    )
    text = models.TextField(
        'Описание рецепта',
    )
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления', validators=[
            MinValueValidator(
                1, message='Минимальное значение 1')]
    )
    pub_date = models.DateTimeField(
        verbose_name="Дата публикации",
        auto_now_add=True,
        editable=False,
    )

    url_link = models.CharField(max_length=128, unique=True)

    def save(self, *args, **kwargs):
        if not self.url_link:
            while True:
                self.url_link = get_random_string(length=8)
                if not Recipe.objects.filter(url_link=self.url_link).exists():
                    break
        super().save(*args, **kwargs)

    class Meta:
        ordering = ('-pub_date', 'id')
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Модель ингредиентов."""

    name = models.CharField(
        'Название ингредиента',
        max_length=128
    )
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=64
    )

    class Meta:
        ordering = ('name', 'id')
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Tag(models.Model):
    """Модель тэгов."""

    name = models.CharField(
        'Тэги', max_length=32,
        help_text='Имя тега'
    )
    slug = models.SlugField(
        'Slug', max_length=32,
        unique=True
    )

    class Meta:
        ordering = ('name', 'id')
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.slug


class RecipeIngredient(models.Model):
    """Промежуточная модель ManyToMany."""

    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='recipe_ingredient_set'
    )
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE,
        verbose_name='Ингредиенты',
        related_name='recipe_ingredient_set'
    )
    amount = models.PositiveSmallIntegerField(
        'Количество', default=1,
        validators=[MinValueValidator(
            1, message='Минимальное значение 1')]
    )

    class Meta:
        verbose_name = 'Ингредиенты рецепта'
        verbose_name_plural = 'Ингредиенты рецептов'

    def __str__(self):
        return f'Ингредиенты {self.ingredient.name} в {self.recipe.name}'


class UserRecipeAbstract(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )

    class Meta:
        abstract = True


class FavoriteRecipe(UserRecipeAbstract):
    """Модель избранных рецептов."""

    class Meta(UserRecipeAbstract.Meta):
        default_related_name = 'favorite_recipes'
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='favorite_recipes',
                violation_error_message='Поля не уникальный.')
                      ]

    def __str__(self):
        return f'Рецепты пользователя: {self.user}'


class ShoppingCart(UserRecipeAbstract):
    """Модель корзины покупок."""

    class Meta(UserRecipeAbstract.Meta):
        default_related_name = 'shopping_carts'
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='shopping_cart_recipe',
                violation_error_message='Поля не уникальный.',
            ),
        ]

    def __str__(self):
        return f'Список покупок пользователя: {self.user}'
