from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, generics, status
from .models import Author, MvIaConceptView, LatamAuthorView, Institution, Work, WorkAuthorship, MvLatamIaConceptView
from .serializers import AuthorSerializer, RecommendationListSerializer, GetRecommendationsRequestSerializer, MvIaConceptViewSerializer, MvLatamIaConceptViewSerializer, InstitutionSerializer, WorkSerializer
from recommender.hybrid_recommender import HybridRecommender
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Q

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
        limit = int(request.query_params.get("limit", 100))
        
        
        if limit <= 0:
            return Response({
                "results": [],
                "next_last_date": None,
                "next_last_id": None,
                "has_more": False
            })
        
        inner = (
            Work.objects
            .filter(authorships__author_id=f"{author_prefix}{author_id}")
            .order_by("-publication_date", "-id")
            .values("id")
            .distinct()[:limit]
        )

        qs = (
            Work.objects
            .filter(id__in=inner)
            .order_by("-publication_date", "-id")
        )

                
        # 🔹 Traer limit + 1 para saber si hay más
        works = list(qs)
        

        serializer = WorkSerializer(works, many=True)
        
        return Response({
            "results": serializer.data,
            "count": len(serializer.data),
        })
# View autocompletado concepts
class ConceptAutocomplete(generics.ListAPIView):
    serializer_class = MvIaConceptViewSerializer

    def get_queryset(self):
        query = self.request.GET.get('search', '')  # obtiene ?search=...
        if query:
            return MvIaConceptView.objects.filter(display_name__istartswith=query)[:10]  
        return MvIaConceptView.objects.none()
    
class MvLatamIaConceptViewAutocomplete(generics.ListAPIView):
    serializer_class = MvLatamIaConceptViewSerializer

    def get_queryset(self):
        query = self.request.GET.get('search', '')
        if query:
            return MvLatamIaConceptView.objects.filter(display_name__istartswith=query)[:10]
        return MvLatamIaConceptView.objects.none()


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
        concept_vector = validated_data.get('concept_vector') or None
        author_id = validated_data.get('author_id') or None

        recommendations = HybridRecommender().get_recommendations(
            user_input=concept_vector,
            author_id=author_id
        )

        # recommendations = [(aid, score), ...]
        top_author_ids = [aid for aid, _ in recommendations]
        scores_dict = {aid: score for aid, score in recommendations}

        # Traemos los datos desde la BD
        authors_qs = LatamAuthorView.objects.filter(id__in=top_author_ids)
        authors_dict = {a.id: a for a in authors_qs}

        # Armamos la respuesta final en el ORDEN original del híbrido
        author_data = []
        for aid in top_author_ids:
            author = authors_dict.get(aid)
            if not author:
                continue  # si no está en la BD, omitelo

            author_data.append({
                "author_id": aid,
                "orcid": author.orcid,
                "display_name": author.display_name,
                "similarity_score": float(scores_dict[aid]),
                "works_count": author.works_count or 0,
                "cited_by_count": author.cited_by_count or 0
            })

        response_data = {
            'total_recommendations': len(recommendations),
            'recommendations': author_data
        }
        
        # 5. Serializar output
        output_serializer = RecommendationListSerializer(response_data)
        
        return Response(
            output_serializer.data,
            status=status.HTTP_200_OK
        )
        