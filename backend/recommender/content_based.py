
# ==============================================================================
# Modelo de recomendaciones de investigadores afines en IA (basado en contenido)
# ==============================================================================

# El modelo provee recomendaciones en base a perfiles conceptuales de los autores (investigadores). Si dos investigadores tienen perfiles conceptuales similares, 
# probablemente tengan intereses de investigación alineados y puedan colaborar de manera natural.

from api.models import WorkConcept, Concept, Author, Institution, LatamAuthorView
from .utils import cosine_similarity
import numpy as np
from django.db.models import Avg, Subquery
from collections import defaultdict
import heapq
import time

class ContentBasedRecommendation:
    """Recommender basado en similitud de conceptos"""

    # Cache de todos los conceptos para no calcularlos de nuevo
    _concepts_cache = None

    # Codigo de Paises
    LATAM_COUNTRIES = [
        'AR', 'BO', 'BR', 'CL', 'CO', 'CR', 'CU', 'DO', 'EC', 'SV', 'GT', 'HN', 'MX', 'NI', 'PA', 'PY', 'PE', 'PR', 'UY', 'VE'
    ]
    
    # Metodo para obtener todos los conceptos
    @classmethod
    def get_all_concepts(cls):
        if cls._concepts_cache is None:
            cls._concepts_cache = list(
                Concept.objects.values_list('id', flat=True).order_by('id')
            )
        return cls._concepts_cache

    # Metodo para construir un vector de conceptos para un autor
    @classmethod
    def build_concept_vector(cls, concept_dict):
        # Query: obtener todos los conceptos en orden
        all_concepts = cls.get_all_concepts() 
        
        # Convertir dict a vector
        vector = np.zeros(len(all_concepts))
        concept_to_idx = {cid: idx for idx, cid in enumerate(all_concepts)}
        
        for concept_id, score in concept_dict.items():
            if concept_id in concept_to_idx:
                vector[concept_to_idx[concept_id]] = score
        
        # Normalizar
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm
        
        return vector

    # Metodo para convertir datos ingresados a vector
    @classmethod
    def convert_vector(cls, input_data):
        # Obtener longitud esperada del vector
        expected_length = len(cls.get_all_concepts())
        
        if isinstance(input_data, str):
            # Si es author_id, obtener sus conceptos
            concept_scores = (
                WorkConcept.objects
                .filter(work__authorships__author_id=input_data)
                .values('concept_id')
                .annotate(avg_score=Avg('score'))
            )
            concept_dict = {cs['concept_id']: cs['avg_score'] for cs in concept_scores}
            return cls.build_concept_vector(concept_dict)
        elif isinstance(input_data, np.ndarray):
            # Validar que el vector tenga la longitud correcta
            if len(input_data) != expected_length:
                raise ValueError(f"Vector debe tener longitud {expected_length}, se recibió {len(input_data)}")
            # Normalizar si es necesario
            norm = np.linalg.norm(input_data)
            if norm > 0:
                return input_data / norm
            return input_data
        else:
            raise ValueError("Input inválido: debe ser author_id (str) o vector de conceptos (np.ndarray)")
    
    # Calcular similitud entre inputs
    @classmethod
    def calculate_similarity(cls, input_1, input_2):
        return cosine_similarity(input_1, input_2)
    

    # Metodo para obtener recomendaciones
    @classmethod
    def get_recommendations(cls, user_input, top_n=20, similarity_threshold=0.1, order_by=None):
        print("Obteniendo recomendaciones...")
        
        start_time = time.perf_counter()  # high-precision timer

        # QUERY 1: Obtener todos los autores LATAM desde la materialized view
        latam_authors_ids = list(
            LatamAuthorView.objects.all().values_list('id', flat=True)
        )

        # Si el usuario ingresa un id entonces esta se agrega a la lista
        if isinstance(user_input, str):
            latam_authors_ids.insert(0, user_input)
        
        # Query 2: Obtenemos todos los conceptos para cada autor
        #recommendations = list(latam_authors_qs)

        end_time = time.perf_counter()
        elapsed = end_time - start_time
        print(f"Tiempo para obtener autores LATAM: {elapsed:.3f} segundos")
        
        return count
