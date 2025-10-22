from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, generics
from .models import Author, Concept, MvIaConceptView
from .serializers import AuthorSerializer, RecommendationListSerializer, GetRecommendationsRequestSerializer, MvIaConceptViewSerializer
from recommender.content_based import ContentBasedRecommendation
from rest_framework.views import APIView
from rest_framework.response import Response

class AuthorViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer

    def get_queryset(self):
        # Limitar a 50 registros para pruebas
        return Author.objects.all()[:50]
    

# View autocompletado concepts
class ConceptAutocomplete(generics.ListAPIView):
    serializer_class = MvIaConceptViewSerializer

    # TODO: evaluar limitar conceptos a los con acestro IA

    def get_queryset(self):
        query = self.request.GET.get('search', '')  # obtiene ?search=...
        if query:
            return MvIaConceptView.objects.filter(display_name__istartswith=query)[:10]  # limitar resultados
        return MvIaConceptView.objects.none()

class RecommendationViewSet(APIView):
    def post(self, request):
        input_serializer = GetRecommendationsRequestSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        data = input_serializer.validated_data
        real_input = data.get('author_id') or data.get('concept_ids')

        recommendations = ContentBasedRecommendation.get_recommendations(            
            user_input=real_input,
            top_n=data['top_n'],
            similarity_threshold=data['similarity_threshold']
        )

        response_data = {
            'total_recommendations' : len(recommendations),
            'recommendations' : recommendations,
            'query_type': 'author_id' if data.get('author_id') else 'concepts' 
        }

        output_serializer = RecommendationListSerializer(response_data)
        return Response(output_serializer.data)