import os
import pickle
import numpy as np
from scipy.sparse import lil_matrix, load_npz
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import normalize

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
        
        # Cargar archivos
        with open(os.path.join(models_dir, 'concept_mapping.pkl'), 'rb') as f:
            concept_to_index = pickle.load(f)
        
        # Cargar matriz sparse normalizada (reemplaza SVD)
        author_matrix = load_npz(os.path.join(models_dir, 'author_concept_matrix.npz'))
        author_ids = np.load(os.path.join(models_dir, 'cb_author_ids.npy'))
        
        # Cargar work counts para Bayesian smoothing
        try:
            author_work_counts = np.load(os.path.join(models_dir, 'cb_author_work_counts.npy'))
        except FileNotFoundError:
            # Fallback si no existe
            author_work_counts = np.ones(len(author_ids), dtype=np.int32)
        
        cls._cache = {
            'concept_to_index': concept_to_index,
            'author_matrix': author_matrix,
            'author_ids': author_ids,
            'author_work_counts': author_work_counts,
            'n_concepts': len(concept_to_index)
        }
    
    @staticmethod
    def create_user_vector(user_concepts, n_concepts, concepts_ids):
        """Método para crear el vector de conceptos del usuario"""
        user_vector = lil_matrix((1, n_concepts), dtype=np.float32)
        
        for concept in user_concepts:
            concept_id = concept['id']
            if concept_id not in concepts_ids:
                continue
            concept_idx = concepts_ids[concept_id]
            user_vector[0, concept_idx] = 1.0
        
        user_vector = user_vector.tocsr()
        # Normalizar L2
        user_vector = normalize(user_vector, norm='l2', axis=1)
        
        return user_vector
    
    @staticmethod
    def apply_bayesian_smoothing(similarities, work_counts, confidence_param=10.0):
        """
        Aplica Bayesian Smoothing a los scores de similitud.
        
        Formula: adjusted_score = raw_score × (n / (n + C))
        
        Donde:
        - n: número de works del autor
        - C: parámetro de confianza (confidence_param)
        
        Ejemplos con C=10 (apropiado para mediana=1, promedio=2.34 works):
        - 1 work:   factor = 0.091 (penaliza 91%)
        - 2 works:  factor = 0.167 (penaliza 83%)
        - 5 works:  factor = 0.333 (penaliza 67%)
        - 10 works: factor = 0.500 (penaliza 50%)
        - 20 works: factor = 0.667 (penaliza 33%)
        - 50 works: factor = 0.833 (penaliza 17%)
        - 100 works: factor = 0.909 (penaliza 9%)
        
        Args:
            similarities: array de scores de similitud
            work_counts: array con número de works por autor
            confidence_param: parámetro C (mayor = más conservador)
                - C=5:  Poco conservador (para datasets con muy pocos works)
                - C=10: Balance recomendado (default, basado en tus datos)
                - C=20: Más conservador
                - C=30: Muy conservador (penaliza mucho autores con <30 works)
        
        Returns:
            array de scores ajustados
        """
        confidence_factor = work_counts / (work_counts + confidence_param)
        return similarities * confidence_factor
    
    @classmethod
    def get_recommendations(cls, user_input):
        """
        Retorna TODOS los autores ordenados por similitud (sin threshold ni top_k).
        
        Args:
            user_input: Lista de conceptos del usuario con formato:
                       [{'id': concept_id}, ...]
        
        Returns:
            Lista de tuplas (author_id, similarity_score) ordenadas descendente
        """
        
        # Inicializar cache si es necesario
        cls._initialize_cache()
        
        concept_to_index = cls._cache['concept_to_index']
        author_matrix = cls._cache['author_matrix']
        author_ids = cls._cache['author_ids']
        author_work_counts = cls._cache['author_work_counts']
        n_concepts = cls._cache['n_concepts']
        
        # Crear vector de usuario normalizado
        user_vector = cls.create_user_vector(user_input, n_concepts, concept_to_index)
        
        # Calcular similitud coseno directamente (sin SVD)
        similarities = cosine_similarity(user_vector, author_matrix)[0]
        
        # Aplicar Bayesian Smoothing
        # Parámetro ajustado a C=10 basado en estadísticas de datos:
        # - Mediana: 1 work, Promedio: 2.34 works
        # - C=10 es apropiado para datasets con muchos autores de pocos works
        # Mayor valor = más conservador (penaliza más a autores con pocos works)
        similarities = cls.apply_bayesian_smoothing(
            similarities, 
            author_work_counts, 
            confidence_param=10.0
        )
        
        # Normalización Gaussiana (Z-Score)
        mean = np.mean(similarities)
        std = np.std(similarities, ddof=0)
        
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