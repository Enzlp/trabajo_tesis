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
        smoothing = 0.005
        user_vector[:] = smoothing
        
        for concept in user_concepts:
            concept_id = concept['id']
            concept_idx = concepts_ids[concept_id]
            user_vector[0, concept_idx] = 1.0
        
        user_vector = user_vector.tocsr()
        return user_vector
    
    @classmethod
    def get_recommendations(cls, user_input):
        """Retorna TODOS los autores ordenados por similitud (sin threshold ni top_k)."""
        
        # Inicializar cache si es necesario
        cls._initialize_cache()
        
        concept_to_index = cls._cache['concept_to_index']
        svd_model = cls._cache['svd_model']
        author_embeddings = cls._cache['author_embeddings']
        author_ids = cls._cache['author_ids']
        n_concepts = cls._cache['n_concepts']
        
        # Crear vector de usuario
        user_vector = cls.create_user_vector(user_input, n_concepts, concept_to_index)
        
        # Obtener embedding del usuario
        user_embedding = svd_model.transform(user_vector.toarray())
        
        # Obtener similitudes con TODOS los autores
        similarities = cosine_similarity(user_embedding, author_embeddings)[0]
        
        # Normalización Gaussiana (Z-Score)
        mean = np.mean(similarities)
        std = np.std(similarities, ddof=0)  # ddof=1 para corrección de muestra
        
        # Manejar caso donde std = 0 (todos los valores iguales)
        if std == 0:
            similarities_norm = np.zeros_like(similarities)
        else:
            similarities_norm = (similarities - mean) / std
        
        # Ordenar *todos* los índices por similitud normalizada descendente
        sorted_indices = np.argsort(-similarities_norm)
        
        sorted_author_ids = author_ids[sorted_indices]
        sorted_scores = similarities_norm[sorted_indices]
        
        # Empaquetar resultados completos
        recommendations = [
            (author_id, float(score))
            for author_id, score in zip(sorted_author_ids, sorted_scores)
        ]
        
        return recommendations
