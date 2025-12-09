from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, generics, status
from .models import Author, MvIaConceptView, LatamAuthorView, Institution, Work, MvLatamIaConceptView, MvLatamIaConceptView, Concept
from .serializers import AuthorSerializer, RecommendationListSerializer, GetRecommendationsRequestSerializer, MvIaConceptViewSerializer, MvLatamIaConceptViewSerializer, InstitutionSerializer, WorkSerializer
from recommender.hybrid_recommender import HybridRecommender
from rest_framework.views import APIView
from rest_framework.response import Response
import math
from recommender.content_based.queries import ContentBasedQueries

from django.db.models import Q
from django.db.models import Func, Value
from django.db.models.fields import CharField

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
# Views autocompletado

import re

def generar_patron_acronimo(query):
    """
    Convierte una cadena corta (ej: 'nlp') en un patrón de regex
    para buscar las iniciales de cada palabra (ej: 'N.*L.*P.*').
    """
    # 1. Asegurarse de que la búsqueda sea insensible a mayúsculas
    query = query.upper()
    
    # 2. Insertar '.*' (cero o más caracteres) entre cada letra.
    # Esto busca: [Inicial1] seguido de cualquier cosa, luego [Inicial2], etc.
    # Ejemplo: 'N.*L.*P.*'
    pattern = '.*'.join(list(query))
    
    # 3. Añadir el marcador de inicio de cadena (si quieres que solo busque al inicio del concepto)
    # o solo usar el patrón. En este caso, buscaremos el acrónimo dentro de la cadena.
    
    return pattern

class ConceptAutocomplete(generics.ListAPIView):
    serializer_class = MvIaConceptViewSerializer

    def get_queryset(self):
        query = self.request.GET.get('search', '')
        
        if not query:
            return MvIaConceptView.objects.none()

        # --- A. Búsqueda por Acrónimo (NLP -> N.*L.*P.*) ---
        acronym_pattern = generar_patron_acronimo(query)

        # 1. Filtro normal (ej: 'Natu' trae 'Natural Language Processing')
        filtro_normal = Q(display_name__istartswith=query)
        
        # 2. Filtro acrónimo (ej: 'nlp' trae 'Natural Language Processing' usando regex)
        # ^ indica el inicio de la cadena, \y indica el límite de palabra.
        # Esto busca las iniciales de las palabras del concepto.
        filtro_acronimo = Q(display_name__iregex=r'\y' + acronym_pattern)

        # 3. Combinar los filtros con OR (|)
        queryset = MvIaConceptView.objects.filter(
            filtro_normal | filtro_acronimo
        ).distinct() # Usamos distinct para evitar duplicados si la búsqueda coincide en ambos filtros
        
        return queryset[:10]

DE_ACENTUADO = 'áéíóúÁÉÍÓÚñÑ'
A_NORMAL = 'aeiouAEIOUnN'

class MvLatamIaConceptViewAutocomplete(generics.ListAPIView):
    serializer_class = MvLatamIaConceptViewSerializer

    def get_queryset(self):
        query = self.request.GET.get('search', '')
        
        if not query:
            return MvLatamIaConceptView.objects.none()

        # 1. Normalizar la columna de la base de datos (Sin cambios)
        columna_normalizada = Func(
            'display_name',
            Value(DE_ACENTUADO),
            Value(A_NORMAL),
            function='TRANSLATE',
            output_field=CharField()
        )

        # 2. Normalizar el término de búsqueda del usuario (Sin cambios)
        # Ejemplo: Si query es 'Hernández', termino_limpio es 'Hernandez'.
        termino_limpio = query.translate(str.maketrans(DE_ACENTUADO, A_NORMAL))
        
        # 3. Construir el filtro para buscar en cualquier parte (icontains)
        # Esto permite buscar por apellido o por cualquier palabra del concepto
        
        return MvLatamIaConceptView.objects.annotate(
            # Anotamos el campo limpiado
            display_name_normalized=columna_normalizada
        ).filter(
            # CAMBIO CLAVE AQUÍ: Usamos __icontains para buscar en cualquier parte del texto.
            # Esto traduce a SQL: ...WHERE display_name_normalized ILIKE '%termino_limpio%'
            display_name_normalized__icontains=termino_limpio
        )[:10]

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

        # Inicializar el caché para obtener el mapeo de conceptos y el vector IDF
        ContentBasedQueries._initialize_cache()
        concept_to_index = ContentBasedQueries._cache['concept_to_index']
        idf_vector = ContentBasedQueries._cache['idf_vector']

        # Si hay filtro por país, traer más candidatos primero
        candidate_limit = 20000 if country_code else limit
        
        # HybridRecommender devuelve:
        # (aid, hybrid_score, cb_score, cf_score)
        recommendations = HybridRecommender().get_recommendations(
            user_input=concept_vector,
            author_id=author_id,
            alpha=alpha,
            beta=beta,
            k=candidate_limit
        )
        
        if not recommendations:
            response_data = {'total_recommendations': 0, 'recommendations': []}
            output_serializer = RecommendationListSerializer(response_data)
            return Response(output_serializer.data, status=status.HTTP_200_OK)

        # Extraer ids y diccionarios de scores
        top_author_ids = [aid for aid, _, _, _ in recommendations]
        hybrid_scores_dict = {aid: score for aid, score, _, _ in recommendations}
        cb_scores_dict = {aid: cb for aid, _, cb, _ in recommendations}
        cf_scores_dict = {aid: cf for aid, _, _, cf in recommendations}

        # FILTRO POR PAÍS
        if country_code:
            valid_author_ids = set(
                LatamAuthorView.objects.filter(
                    id__in=top_author_ids,
                    country_code=country_code
                ).values_list('id', flat=True)
            )

            recommendations = [
                (aid, hybrid_score, cb_score, cf_score)
                for aid, hybrid_score, cb_score, cf_score in recommendations
                if aid in valid_author_ids
            ]

            if not recommendations:
                response_data = {'total_recommendations': 0, 'recommendations': []}
                output_serializer = RecommendationListSerializer(response_data)
                return Response(output_serializer.data, status=status.HTTP_200_OK)

        # Actualizar IDs tras filtrado
        top_author_ids = [aid for aid, _, _, _ in recommendations]

        # Query autores
        authors_dict = LatamAuthorView.objects.filter(
            id__in=top_author_ids
        ).only(
            'id','orcid','display_name','works_count','cited_by_count',
            'country_code','institution_name'
        ).in_bulk()

        # ORDENAMIENTO
        if order_by == 'works':
            recommendations = sorted(
                recommendations,
                key=lambda x: (
                    -(authors_dict.get(x[0]).works_count or 0),
                    -x[1]
                )
            )

        elif order_by == 'cites':
            recommendations = sorted(
                recommendations,
                key=lambda x: (
                    -(authors_dict.get(x[0]).cited_by_count or 0),
                    -x[1]
                )
            )

        # Aplicar límite final
        recommendations = recommendations[:limit]

        # Regenerar diccionarios finales
        top_author_ids = [aid for aid, _, _, _ in recommendations]
        hybrid_scores_dict = {aid: s for aid, s, _, _ in recommendations}
        cb_scores_dict = {aid: cb for aid, _, cb, _ in recommendations}
        cf_scores_dict = {aid: cf for aid, _, _, cf in recommendations}

        # Query conceptos top-3 por autor (TF-IDF sublineal)
        concept_rows = MvLatamIaConceptView.objects.filter(
            author_id__in=top_author_ids
        )

        all_concept_ids = set()
        top_concepts_temp = {}

        for row in concept_rows:

            raw_pairs = zip(row.concept_ids, row.concept_tfs)

            tfidf_scores = []

            for concept_id, raw_tf in raw_pairs:
                if concept_id not in concept_to_index:
                    continue

                concept_idx = concept_to_index[concept_id]

                tf_value = float(raw_tf)
                tf_sub = 1 + math.log(tf_value) if tf_value > 0 else 0

                idf_w = idf_vector[concept_idx]
                tfidf_score = tf_sub * idf_w

                if tfidf_score > 0:
                    tfidf_scores.append((concept_id, tfidf_score))

            pairs = sorted(tfidf_scores, key=lambda x: x[1], reverse=True)[:3]
            top_concepts_temp[row.author_id] = pairs

            for cid, _ in pairs:
                all_concept_ids.add(cid)

        concept_objects = Concept.objects.filter(id__in=all_concept_ids).only("id", "display_name")
        concept_name_map = {c.id: c.display_name for c in concept_objects}

        concepts_dict = {}
        for author_id, pairs in top_concepts_temp.items():
            concepts_dict[author_id] = [
                {
                    "concept_id": cid,
                    "score": float(score),
                    "display_name": concept_name_map.get(cid)
                }
                for cid, score in pairs
            ]

        # Construcción final del payload
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
                    "similarity_score": float(hybrid_scores_dict[aid]),  # Score híbrido
                    "cb_score": float(cb_scores_dict[aid]),              # Score del content-based
                    "cf_score": float(cf_scores_dict[aid]),              # Score del collaborative filtering
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


class AuthorConceptsView(APIView):
    """
    GET /api/authors/<author_id>/concepts/
    Devuelve los conceptos asociados al autor
    """
    def get(self, request, author_id):
        author_prefix = "https://openalex.org/"
        concept_ids = (
            MvLatamIaConceptView.objects
            .filter(author_id=f"{author_prefix}{author_id}")
            .values_list("concept_ids", flat=True)
            .first()
        )

        if concept_ids is None:
            return Response(
                {"error": "Autor no encontrado."},
                status=status.HTTP_404_NOT_FOUND
            )

        concepts = Concept.objects.filter(id__in=concept_ids).values("id", "display_name")

        return Response(list(concepts), status=status.HTTP_200_OK)

