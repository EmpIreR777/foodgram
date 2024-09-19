from django.urls import path, include
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView)

from .views import (
    UserViewSet,
    TagViewSet,
    RecipeViewSet,
    IngredientViewSet)
    # RecipeByShortCodeDetailView)


v1_router = DefaultRouter()

v1_router.register(r'users',
                   UserViewSet, basename='users')
v1_router.register(r'tags',
                   TagViewSet, basename='tags')
v1_router.register(r'ingredients',
                   IngredientViewSet, basename='ingredients')
v1_router.register(r'recipes',
                   RecipeViewSet, basename='recipes')

urlpatterns = [
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(v1_router.urls)),
    # path('recipes/s/<str:short_code>/',
    #      RecipeByShortCodeDetailView.as_view(), name='short_code'),
    path("schema/", SpectacularAPIView.as_view(),
         name="schema"),
    path("schema/redoc/", SpectacularRedocView.as_view(
        url_name="schema"), name="redoc"),
    path("schema/swagger-ui/", SpectacularSwaggerView.as_view(
        url_name="schema"), name="swagger-ui"),
]
