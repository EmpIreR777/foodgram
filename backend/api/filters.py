from rest_framework.filters import SearchFilter
from django_filters.rest_framework import filters, FilterSet

from recipes.models import Recipe, Ingredient


class IngredientSearchFilter(SearchFilter):
    search_param = 'name'

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(FilterSet):
    is_favorited = filters.NumberFilter(
        method='get_favorite_recipes')
    is_in_shopping_cart = filters.NumberFilter(
        method='get_is_in_shopping_cart')
    tags = filters.AllValuesMultipleFilter(
        field_name='tags__slug')

    class Meta:
        model = Recipe
        fields = ('author', 'is_favorited', 'is_in_shopping_cart', 'tags')

    def get_is_in_shopping_cart(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(shopping_carts__user=self.request.user)
        return queryset

    def get_favorite_recipes(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(favorite_recipes__user=self.request.user)
        return queryset
