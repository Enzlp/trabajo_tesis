from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, generics, status
from .models import Author, MvIaConceptView, LatamAuthorView, Institution, Work, WorkAuthorship
from .serializers import AuthorSerializer, RecommendationListSerializer, GetRecommendationsRequestSerializer, MvIaConceptViewSerializer, LatamAuthorViewSerializer, InstitutionSerializer, WorkSerializer
from recommender.content_based import ContentBasedRecommendation
from rest_framework.views import APIView
from rest_framework.response import Response

class AuthorViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer

    def get_queryset(self):
        queryset = Author.objects.all()

        author_id = self.request.query_params.get('id')
        if author_id:
            return queryset.filter(id=author_id)

        return Author.objects.all()[:50]
    
class InstitutionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Institution.objects.all()
    serializer_class = InstitutionSerializer

    def get_queryset(self):
        queryset = Institution.objects.all()

        institution_id = self.request.query_params.get('id')
        if institution_id:
            return queryset.filter(id=institution_id)
        return
    
# View para works de un autor
class AuthorWorksView(APIView):
    def get(self, request, author_id: str):
        author_prefix = "https://openalex.org/"
        limit = int(request.query_params.get("limit", 50))
        last_work_id = request.query_params.get("last_work_id")

        qs = WorkAuthorship.objects.filter(author_id=f"{author_prefix}{author_id}")
        if last_work_id:
            qs = qs.filter(work_id__gt=last_work_id)

        qs = qs.order_by("work_id").values_list("work_id", flat=True)[:limit]
        work_ids = list(qs)

        works = Work.objects.filter(id__in=work_ids)
        
        serializer = WorkSerializer(works, many=True)


        return Response({
            "results": serializer.data,
            "next_last_work_id": work_ids[-1] if work_ids else None
        })

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