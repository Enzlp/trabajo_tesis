from rest_framework import serializers
from .models import Author, MvIaConceptView

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


# Serializer autocompletado concepts
class MvIaConceptViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = MvIaConceptView
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
    query_type = serializers.CharField()
    
class GetRecommendationsRequestSerializer(serializers.Serializer):
    """
    Serializer para validar el input del usuario.
    """
    author_id = serializers.CharField(required=False, allow_blank=True)
    concept_ids = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )
    top_n = serializers.IntegerField(default=10, min_value=1, max_value=50)
    similarity_threshold = serializers.FloatField(
        default=0.1, 
        min_value=0.0, 
        max_value=1.0
    )
    
    def validate(self, data):
        """Validar que se proporciona author_id O concept_ids"""
        author_id = data.get('author_id')
        concept_ids = data.get('concept_ids')
        
        if not author_id and not concept_ids:
            raise serializers.ValidationError(
                "Debes proporcionar 'author_id' o 'concept_ids'"
            )
        
        if author_id and concept_ids:
            raise serializers.ValidationError(
                "Proporciona solo 'author_id' o 'concept_ids', no ambos"
            )
        
        return data