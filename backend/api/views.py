from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, generics, status
from .models import Author, Concept, MvIaConceptView, LatamAuthorView
from .serializers import AuthorSerializer, RecommendationListSerializer, GetRecommendationsRequestSerializer, MvIaConceptViewSerializer, LatamAuthorViewSerializer
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

    def get_queryset(self):
        query = self.request.GET.get('search', '')  # obtiene ?search=...
        if query:
            return MvIaConceptView.objects.filter(display_name__istartswith=query)[:10]  
        return MvIaConceptView.objects.none()
    
class LatamAuthorAutocomplete(generics.ListAPIView):
    serializer_class = LatamAuthorViewSerializer

    def get_queryset(self):
        query = self.request.GET.get('search', '')
        if query:
            return LatamAuthorView.objects.filter(display_name__istartswith=query)[:10]
        return LatamAuthorView.objects.none()


class RecommendationViewSet(APIView):
    """
    API endpoint para obtener recomendaciones de autores
    basadas en conceptos de interés del usuario.
    """
    
    def post(self, request):
        # 1. Validar input
        input_serializer = GetRecommendationsRequestSerializer(data=request.data)
        
        if not input_serializer.is_valid():
            return Response(
                {
                    'error': 'Datos inválidos',
                    'details': input_serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 2. Obtener datos validados
        validated_data = input_serializer.validated_data
        concept_vector = validated_data['concept_vector']
        
        try:
            # 3. Llamar al sistema de recomendación
            recommendations = ContentBasedRecommendation.get_recommendations(
                user_input=concept_vector
            )
            
            # 4. Preparar respuesta
            response_data = {
                'total_recommendations': len(recommendations),
                'recommendations': recommendations
            }
            
            # 5. Serializar output
            output_serializer = RecommendationListSerializer(response_data)
            
            return Response(
                output_serializer.data,
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            return Response(
                {
                    'error': 'Error al generar recomendaciones',
                    'details': str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )