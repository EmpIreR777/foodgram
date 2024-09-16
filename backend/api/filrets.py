from django_filters import rest_framework as filters
from recipes.models import Recipe, Tag


class RecipeFilter(filters.FilterSet):
    tags = filters.ModelMultipleChoiceFilter(
        field_name="tags__slug", lookup_expr='icontains',
        to_field_name='slug', queryset=Tag.objects.all()
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart')
    is_favorited = filters.BooleanFilter(
        method='filter_is_favorited')

    class Meta:
        model = Recipe
        fields = {
            'author',
            'tags',
        }

    def filter_is_favorited(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(
                favoriterecipe__user=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(in_cart__user=self.request.user)
        return queryset
