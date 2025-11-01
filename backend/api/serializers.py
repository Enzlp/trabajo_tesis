from rest_framework import serializers
from .models import Author, MvIaConceptView, LatamAuthorView, Institution, Work
class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = [
            "id",
            "orcid",
            "display_name",
            "display_name_alternatives",
            "works_count",
            "cited_by_count",
            "last_known_institution",
            "works_api_url",
            "updated_date"
        ]

class InstitutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Institution
        fields = [
            "id",
            "display_name",
            "homepage_url"
        ]

class WorkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Work
        fields = [
            "id",
            "doi",
            "title" ,
            "display_name" ,
            "publication_year",
            "publication_date",
            "type" ,
            "cited_by_count",
            "is_retracted",
            "is_paratext",
            "language"
        ]

# Serializer autocompletado concepts
class MvIaConceptViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = MvIaConceptView
        fields = [
            "id",
            "display_name"
        ]

# Serializer autocompletado de autores
class LatamAuthorViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = LatamAuthorView
        fields = [
            "id",
            "display_name"
        ]

# Serializers para recommendaciones
class RecommendationSerializer(serializers.Serializer):
    author_id = serializers.CharField()
    orcid = serializers.CharField()
    display_name = serializers.CharField()
    similarity_score = serializers.FloatField()
    works_count = serializers.IntegerField()
    cited_by_count = serializers.IntegerField()

class RecommendationListSerializer(serializers.Serializer):
    total_recommendations = serializers.IntegerField()
    recommendations = RecommendationSerializer(many=True)
    
class ConceptInputSerializer(serializers.Serializer):
    """Valida cada concepto individualmente"""
    id = serializers.CharField(
        max_length=100,
        required=True,
        help_text="ID del concepto de OpenAlex (ej: C41008148)"
    )
    display_name = serializers.CharField(
        max_length=200,
        required=True,
        help_text="Nombre del concepto (ej: Machine Learning)"
    )


class GetRecommendationsRequestSerializer(serializers.Serializer):
    """Valida el input completo del usuario"""
    concept_vector = serializers.ListField(
        child=ConceptInputSerializer(),
        min_length=1,
        max_length=100,
        help_text="Lista de conceptos de interés del usuario"
    )
