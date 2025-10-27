
# ==============================================================================
# Modelo de recomendaciones de investigadores afines en IA (basado en contenido)
# ==============================================================================

# El modelo provee recomendaciones en base a perfiles conceptuales de los autores (investigadores). Si dos investigadores tienen perfiles conceptuales similares, 
# probablemente tengan intereses de investigación alineados y puedan colaborar de manera natural.

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
import django
django.setup()

from api.models import LatamAuthorView
import numpy as np
from scipy.sparse import lil_matrix
import pickle
import joblib
from pathlib import Path
from sklearn.preprocessing import normalize
from sklearn.metrics.pairwise import cosine_similarity

class ContentBasedRecommendation:
    """Recommender basado en similitud de conceptos"""

    # Cache de todos los conceptos para no calcularlos de nuevo
    _concepts_cache = None

    # Codigo de Paises
    LATAM_COUNTRIES = [
        'AR', 'BO', 'BR', 'CL', 'CO', 'CR', 'CU', 'DO', 'EC', 'SV', 'GT', 'HN', 'MX', 'NI', 'PA', 'PY', 'PE', 'PR', 'UY', 'VE'
    ]

    # Metodo para cargar los datos precalculados
    @staticmethod
    def load_models(models_dir):
        # Mapeo de conceptos
        with open(models_dir / 'concept_mapping.pkl', 'rb') as f:
            concept_to_index = pickle.load(f)

        # Modelo SVD
        svd_model = joblib.load(models_dir / 'svd_model.pkl')

        # Modelo embeddings autor
        author_embeddings = np.load(models_dir / 'author_embeddings.npy')

        # IDs de autores
        author_ids = np.load(models_dir / 'author_ids.npy')

        return concept_to_index, svd_model, author_embeddings, author_ids
    
    # Metodo para cacular el vector de conceptos del usuario
    @staticmethod
    def create_user_vector(user_concepts, n_concepts, concept_to_index):

        user_vector = lil_matrix((1, n_concepts), dtype=np.float32)
        smoothing = 0.01
        user_vector[:] = smoothing  # un valor mínimo para todos los conceptos

        for concept in user_concepts:
            concept_id = concept['id']
            concept_idx = concept_to_index[concept_id]
            user_vector[0, concept_idx] = 1.0  # refuerza los conceptos seleccionados

        user_vector = user_vector.tocsr()

        return user_vector

    # Metodo para obtener recomendaciones
    @classmethod
    def get_recommendations(cls, user_input, top_k=40, similarity_threshold=0.1, order_by=None):

        # Cargar modelos
        models_dir = Path("recommender/files")
        concept_to_index, svd_model, author_embeddings, author_ids = cls.load_models(models_dir)
        n_concepts = len(concept_to_index)

        # Calcular vectores
        user_vector = cls.create_user_vector(user_input, n_concepts,concept_to_index)

        # Normalizamos vector de usuario y transformamos a svd
        user_vector_normalized = normalize(user_vector, norm='l2', axis=1)
        user_embedding = svd_model.transform(user_vector_normalized.toarray())

        # Calcular similaridad
        similarities = cosine_similarity(user_embedding, author_embeddings)[0]

        # Se obtienen las top k recomendaciones
        top_indices = np.argsort(similarities)[-top_k:][::-1]

        # Preparan resultados
        top_author_ids = author_ids[top_indices].tolist()
        #print(top_author_ids)
        #print(similarities[top_indices[len(top_indices)-1]])
        
        authors = LatamAuthorView.objects.filter(id__in=top_author_ids)
        authors_dict = {a.id: a for a in authors}

        recommendations = []
        for i, author_id in enumerate(top_author_ids):
            a_info = authors_dict.get(author_id)
            if a_info:
                recommendations.append({
                    "author_id": author_id,
                    'orcid': getattr(a_info, 'orcid', None),
                    "display_name": a_info.display_name,
                    'similarity_score': float(similarities[top_indices[i]]),
                    'works_count': getattr(a_info, 'works_count', 0),
                    'cited_by_count': getattr(a_info, 'cited_by_count', 0)
                })

        return recommendations
