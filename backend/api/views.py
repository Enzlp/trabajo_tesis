from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, generics, status
from .models import Author, MvIaConceptView, LatamAuthorView, Institution, Work, MvLatamIaConceptView, MvLatamIaConceptView, Concept
from .serializers import AuthorSerializer, RecommendationListSerializer, GetRecommendationsRequestSerializer, MvIaConceptViewSerializer, MvLatamIaConceptViewSerializer, InstitutionSerializer, WorkSerializer
from recommender.hybrid_recommender import HybridRecommender
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
        input_serializer = GetRecommendationsRequestSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        
        validated_data = input_serializer.validated_data
        concept_vector = validated_data.get('concept_vector')
        author_id = validated_data.get('author_id')
        alpha = validated_data.get('alpha', 0.5)
        beta = validated_data.get('beta', 0.5)
        limit = validated_data.get('limit', 50)
        country_code = validated_data.get('country_code', '')
        order_by = validated_data.get('order_by', 'sim')
        
        # 🔹 Traer más candidatos si hay filtro de país (para compensar el filtrado)
        candidate_limit = 20000 if country_code else limit
        
        recommendations = HybridRecommender().get_recommendations(
            user_input=concept_vector,
            author_id=author_id,
            alpha=alpha,
            beta=beta,
            k=candidate_limit
        )
        
        if not recommendations:
            response_data = {
                'total_recommendations': 0,
                'recommendations': []
            }
        else:
            top_author_ids = [aid for aid, _ in recommendations]
            
            # 🔹 FILTRADO POR PAÍS (si se especifica)
            if country_code:
                # Query eficiente: solo traer IDs de autores del país
                valid_author_ids = set(
                    LatamAuthorView.objects.filter(
                        id__in=top_author_ids,
                        country_code=country_code
                    ).values_list('id', flat=True)
                )
                
                # Filtrar recomendaciones manteniendo el orden y score
                recommendations = [
                    (aid, score) for aid, score in recommendations 
                    if aid in valid_author_ids
                ]
                
                if not recommendations:
                    response_data = {
                        'total_recommendations': 0,
                        'recommendations': []
                    }
                    output_serializer = RecommendationListSerializer(response_data)
                    return Response(output_serializer.data, status=status.HTTP_200_OK)
            
            # 🔹 Actualizar top_author_ids DESPUÉS del filtro
            top_author_ids = [aid for aid, _ in recommendations]
            
            # --- Query 1: autores (traer métricas para reordenamiento) ---
            # 🔹 IMPORTANTE: Traer TODOS los autores candidatos antes de reordenar
            authors_dict = LatamAuthorView.objects.filter(
                id__in=top_author_ids
            ).only(
                'id','orcid','display_name','works_count','cited_by_count',
                'country_code','institution_name'
            ).in_bulk()

            # 🔹 REORDENAMIENTO POR MÉTRICAS (si se especifica)
            if order_by == 'works':
                # Reordenar por works_count descendente, manteniendo similarity como desempate
                recommendations = sorted(
                    recommendations,
                    key=lambda x: (
                        -(authors_dict.get(x[0]).works_count or 0) if authors_dict.get(x[0]) else 0,
                        -x[1]
                    )
                )
            elif order_by == 'cites':
                # Reordenar por cited_by_count descendente, manteniendo similarity como desempate
                recommendations = sorted(
                    recommendations,
                    key=lambda x: (
                        -(authors_dict.get(x[0]).cited_by_count or 0) if authors_dict.get(x[0]) else 0,
                        -x[1]
                    )
                )

            if order_by in ['works', 'cites']:
                print(f"\n🔍 Top 10 después de ordenar por {order_by}:")
                for i, (aid, score) in enumerate(recommendations[:10]):
                    author = authors_dict.get(aid)
                    if author:
                        print(f"{i+1}. {author.display_name}: "
                            f"works={author.works_count}, "
                            f"cites={author.cited_by_count}, "
                            f"sim={score:.4f}")
            
            # 🔹 AHORA SÍ aplicar el límite final después del reordenamiento
            recommendations = recommendations[:limit]
            top_author_ids = [aid for aid, _ in recommendations]
            scores_dict = {aid: score for aid, score in recommendations}

            # --- Query 2: conceptos (top-3 por autor) ---
            concept_rows = MvLatamIaConceptView.objects.filter(
                author_id__in=top_author_ids
            )

            # Extraer todos los concept_ids que aparecerán en el top 3
            all_concept_ids = set()
            top_concepts_temp = {}

            for row in concept_rows:
                pairs = sorted(
                    zip(row.concept_ids, row.concept_scores),
                    key=lambda x: x[1],
                    reverse=True
                )[:3]  # top 3
                
                top_concepts_temp[row.author_id] = pairs
                
                for cid, _ in pairs:
                    all_concept_ids.add(cid)

            # --- Query 3: nombres de conceptos ---
            concept_objects = Concept.objects.filter(id__in=all_concept_ids).only("id", "display_name")
            concept_name_map = {c.id: c.display_name for c in concept_objects}

            # Reemplazar por objetos finales con display_name
            concepts_dict = {}
            for author_id, pairs in top_concepts_temp.items():
                concepts_dict[author_id] = [
                    {
                        "concept_id": cid,
                        "score": float(score),
                        "display_name": concept_name_map.get(cid, None)
                    }
                    for cid, score in pairs
                ]

            # --- Construir respuesta final ---
            author_data = []
            for aid in top_author_ids:
                author = authors_dict.get(aid)
                if author:
                    author_data.append({
                        "author_id": aid,
                        "orcid": author.orcid,
                        "display_name": author.display_name,
                        "country_code": author.country_code,
                        "institution_name": author.institution_name,
                        "similarity_score": float(scores_dict[aid]),
                        "works_count": author.works_count or 0,
                        "cited_by_count": author.cited_by_count or 0,
                        "top_concepts": concepts_dict.get(aid, [])
                    })

            response_data = {
                'total_recommendations': len(recommendations),
                'recommendations': author_data
            }

        output_serializer = RecommendationListSerializer(response_data)
        return Response(output_serializer.data, status=status.HTTP_200_OK)