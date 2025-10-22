from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AuthorViewSet, RecommendationViewSet, ConceptAutocomplete

router = DefaultRouter()
router.register(r'author', AuthorViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('recommendation/', RecommendationViewSet.as_view(), name='recommendation'),
    path('concept/', ConceptAutocomplete.as_view(), name='concept-autocomplete'),
]