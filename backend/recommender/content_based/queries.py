import os
import pickle
import joblib
import numpy as np
from scipy.sparse import lil_matrix
from sklearn.metrics.pairwise import cosine_similarity

class ContentBasedQueries:
    # Cache estático a nivel de clase
    _cache = None
    
    @classmethod
    def _initialize_cache(cls):
        """Inicializa el cache una sola vez"""
        if cls._cache is not None:
            return
        
        models_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
            "files"
        )
        
        # Cargar todo una sola vez
        with open(os.path.join(models_dir, 'concept_mapping.pkl'), 'rb') as f:
            concept_to_index = pickle.load(f)
        
        svd_model = joblib.load(os.path.join(models_dir, 'svd_model.pkl'))
        author_embeddings = np.load(os.path.join(models_dir, 'cb_author_embeddings.npy'))
        author_ids = np.load(os.path.join(models_dir, 'cb_author_ids.npy'))
        
        cls._cache = {
            'concept_to_index': concept_to_index,
            'svd_model': svd_model,
            'author_embeddings': author_embeddings,
            'author_ids': author_ids,
            'n_concepts': len(concept_to_index)
        }
    
    @staticmethod
    def create_user_vector(user_concepts, n_concepts, concepts_ids):
        """Método para crear el vector de conceptos del usuario"""
        user_vector = lil_matrix((1, n_concepts), dtype=np.float32)
        smoothing = 0.12
        user_vector[:] = smoothing
        
        for concept in user_concepts:
            concept_id = concept['id']
            concept_idx = concepts_ids[concept_id]
            user_vector[0, concept_idx] = 1.0
        
        user_vector = user_vector.tocsr()
        return user_vector
    
    @classmethod
    def get_recommendations(cls, user_input, top_k=20, similarity_threshold=0.2):
        """Método para obtener el listado de recomendaciones basados en el vector de conceptos de usuario"""
        # Inicializar cache si es necesario
        cls._initialize_cache()
        
        # Usar datos del cache
        concept_to_index = cls._cache['concept_to_index']
        svd_model = cls._cache['svd_model']
        author_embeddings = cls._cache['author_embeddings']
        author_ids = cls._cache['author_ids']
        n_concepts = cls._cache['n_concepts']
        
        # Crear vector de usuario
        user_vector = cls.create_user_vector(user_input, n_concepts, concept_to_index)
        
        # Crear embeddings de usuario
        user_embedding = svd_model.transform(user_vector.toarray())
        
        # Calcular similitudes
        similarities = cosine_similarity(user_embedding, author_embeddings)[0]
        
        # Filtrar por umbral
        filtered_indices = np.where(similarities >= similarity_threshold)[0]
        if len(filtered_indices) == 0:
            return []
        
        # Top-K eficiente con argpartition
        k = min(top_k, len(filtered_indices))
        top_indices_local = np.argpartition(-similarities[filtered_indices], k-1)[:k]
        top_indices_local = top_indices_local[np.argsort(-similarities[filtered_indices][top_indices_local])]
        top_indices = filtered_indices[top_indices_local]
        
        # Obtener author IDs y scores
        top_author_ids = author_ids[top_indices]
        raw_scores = similarities[top_indices]
        
        
        # Empaquetar resultado
        recommendations = [
            (author_id, float(raw_score))
            for author_id, raw_score in zip(top_author_ids, raw_scores)
        ]
        
        return recommendations