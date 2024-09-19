from django.http import JsonResponse
from rest_framework.generics import get_object_or_404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.generics import RetrieveAPIView
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as CustomUser

from .filters import RecipeFilter, IngredientSearchFilter
from users.models import User
from recipes.models import (
    Tag, Ingredient, Recipe,
    FavoriteRecipe, ShoppingCart)
from .permissions import IsStaffOrIsAuthorOrReadOnly
from .pagination import PagePagination
from .serializers import (
    UserSerializer,
    AvatarSerializer,
    TagSerializer,
    IngredientSerializer,
    RecipeReadSerializer,
    RecipeCreateUpdateSerializer,
    FavoriteRecipeSerializer,
    ShoppingCartSerializer,
    SubscriptionsSerializer,
    SubscribeSerializer,
)
from .pdf import create_ingredients_list, create_pdf


class RecipeViewSet(ModelViewSet):
    """Вьюсет рецептов favorit/ shopping_cart/ download_shopping_cart/"""

    permission_classes = (IsStaffOrIsAuthorOrReadOnly,)
    http_method_names = ('get', 'post', 'patch', 'delete')
    pagination_class = PagePagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_queryset(self):
        return Recipe.objects.select_related(
            'author').prefetch_related('ingredients', 'tags')

    def get_serializer_class(self, *args, **kwargs):
        if self.action in ('list', 'retrieve'):
            return RecipeReadSerializer
        return RecipeCreateUpdateSerializer

    @staticmethod
    def add_method(serializer_cls, request, pk):
        serializer = serializer_cls(data={
            'user': request.user.id, 'recipe': pk}, context={
                'request': request})
        if not Recipe.objects.filter(id=pk).exists():
            return Response(data={
                'error': 'Вы пытаетесь добавить несуществующий рецепт'},
                status=status.HTTP_404_NOT_FOUND)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def delete_method(model, request, pk):
        if not Recipe.objects.filter(id=pk).exists():
            return Response(
                data={
                    'error': 'Вы пытаетесь удалить несуществующий рецепт'},
                status=status.HTTP_404_NOT_FOUND
            )
        del_item, item = model.objects.filter(
            user=request.user, recipe=pk).delete()
        if del_item:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response('Нет в добавленных.',
                        status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=('get',), url_path='get-link')
    def get_link(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        url_link = f'https://foodgram-best.zapto.org/recipes/s/{
            recipe.url_link}'
        return JsonResponse({'short-link': url_link})

    @action(detail=True, methods=('post',),
            permission_classes=(IsAuthenticated,))
    def favorite(self, request, pk):
        return self.add_method(FavoriteRecipeSerializer, request, pk)

    @favorite.mapping.delete
    def delete_favorite(self, request, pk):
        return self.delete_method(FavoriteRecipe, request, pk)

    @action(detail=True, methods=('post',),
            permission_classes=(IsAuthenticated,))
    def shopping_cart(self, request, pk):
        return self.add_method(ShoppingCartSerializer, request, pk)

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk):
        return self.delete_method(ShoppingCart, request, pk)

    @action(methods=('get',), detail=False,
            permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        final_list = create_ingredients_list(request)
        pdf_response = create_pdf(final_list, "ingredients_list.pdf")
        return pdf_response


class IngredientViewSet(ReadOnlyModelViewSet):
    """Вьюсет ингредиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (IngredientSearchFilter,)
    search_fields = ('^name',)


class TagViewSet(ReadOnlyModelViewSet):
    """Вьюсет тэгов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)


class UserViewSet(CustomUser):
    """Вьюсет юзера urls = user/ me/ sub/ me/avatar/."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = PagePagination

    @action(detail=True, methods=['post'],
            permission_classes=(IsAuthenticated,))
    def subscribe(self, request, id):
        user = request.user
        serializer = SubscribeSerializer(
            data={
                'user': user.id,
                'following': id},
            context={'request': request})
        if not User.objects.filter(id=self.kwargs['id']).exists():
            return Response(
                data={
                    'Вы пытаетесь подписатсья на несуществующего юзера',
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)

    @subscribe.mapping.delete
    def delete_subscribe(self, request, id):
        if not User.objects.filter(id=id).exists():
            return Response(
                data={
                    'Вы пытаетесь удалить несуществующего подписчика',
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        del_item, item = request.user.follower.filter(
            following=id).delete()
        if del_item:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response('Нет в добавленных.',
                        status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=('get',),
            permission_classes=(IsAuthenticated,))
    def subscriptions(self, request):
        queryset = User.objects.filter(
            following__user=self.request.user)
        pag = self.paginate_queryset(queryset)
        serializer = SubscriptionsSerializer(
            pag, context={'request': request}, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False, methods=('put',), url_path='me/avatar',
            permission_classes=(IsAuthenticated,))
    def update_avatar(self, request):
        serializer = AvatarSerializer(request.user, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data,
                            status=status.HTTP_200_OK)
        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)

    @update_avatar.mapping.delete
    def delete_avatar(self, request):
        request.user.avatar.delete()
        request.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=('get',),
            permission_classes=(IsAuthenticated,))
    def me(self, request):
        serializer = UserSerializer(
            request.user, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class RecipeByShortCodeDetailView(RetrieveAPIView):
    """Вьюсет обработки короткой ссылки."""

    queryset = Recipe.objects.all()
    serializer_class = RecipeReadSerializer
    lookup_field = 'url_link'
    lookup_url_kwarg = 'short_code'
