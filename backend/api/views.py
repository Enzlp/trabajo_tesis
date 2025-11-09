from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, generics, status
from .models import Author, MvIaConceptView, LatamAuthorView, Institution, Work, WorkAuthorship
from .serializers import AuthorSerializer, RecommendationListSerializer, GetRecommendationsRequestSerializer, MvIaConceptViewSerializer, LatamAuthorViewSerializer, InstitutionSerializer, WorkSerializer
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
        limit = int(request.query_params.get("limit", 10))
        last_date = request.query_params.get("last_date")
        last_id = request.query_params.get("last_id")

        # 🔹 Máximo total de 100 trabajos
        max_records = 100

        # 🔹 Query base: solo los trabajos del autor
        qs = Work.objects.filter(authorships__author_id=f"{author_prefix}{author_id}")

        # 🔹 Ordenar por fecha (más recientes primero)
        qs = qs.order_by("-publication_date", "-id")

        # 🔹 Paginación con cursor: continuar desde el último trabajo mostrado
        if last_date and last_id:
            qs = qs.filter(
                Q(publication_date__lt=last_date)
                | Q(publication_date=last_date, id__lt=last_id)
            )

        # 🔹 Traer limit + 1 para saber si hay más
        works = list(qs[:limit + 1])

        # 🔹 Quitar duplicados manualmente (por si hay algún cruce)
        unique_works = []
        seen_ids = set()
        for w in works:
            if w.id not in seen_ids:
                seen_ids.add(w.id)
                unique_works.append(w)
        works = unique_works

        # 🔹 Determinar si hay más resultados
        has_more = len(works) > limit
        works = works[:limit]

        serializer = WorkSerializer(works, many=True)

        total_sent = int(request.query_params.get("total_sent", 0))
        reached_max = total_sent + len(works) >= max_records

        # 🔹 Preparar el cursor para la siguiente página
        next_last_date = None
        next_last_id = None
        if has_more and not reached_max and works:
            last_work = works[-1]
            next_last_date = last_work.publication_date
            next_last_id = last_work.id

        return Response({
            "results": serializer.data,
            "next_last_date": next_last_date,
            "next_last_id": next_last_id,
            "has_more": has_more and not reached_max
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
        