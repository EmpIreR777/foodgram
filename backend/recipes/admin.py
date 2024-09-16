from django.contrib import admin

from .models import (Tag, Ingredient, Recipe, 
                     FavoriteRecipe, ShoppingCart, RecipeIngredient)


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient', 'amount')
    list_filter = ('recipe', 'ingredient')


class IngredientInline(admin.StackedInline):
    model = RecipeIngredient
    extra = 3
    min_num = 1


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    list_filter = ('name', 'slug')
    search_fields = ('slug',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    list_filter = ('name', 'measurement_unit')
    search_fields = ('slug',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'author', 'image', 'url_link')
    list_display_links = ('id', 'name', 'author')
    list_filter = (
        'author',
        'name',
        'tags',
    )
    ordering = ('author',)
    raw_id_fields = ('author', 'tags', 'ingredients')
    inlines = (IngredientInline,)


@admin.register(FavoriteRecipe)
class FavoriteRecipeAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    list_filter = ('user', 'recipe')
    search_fields = ('user',)
    empty_value_display = '-пусто-'


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    list_filter = ('user', 'recipe')
    search_fields = ('user',)
    empty_value_display = '-пусто-'
