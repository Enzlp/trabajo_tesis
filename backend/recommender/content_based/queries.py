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
        
        author_matrix = load_npz(os.path.join(models_dir, 'author_concept_matrix.npz'))
        author_ids = np.load(os.path.join(models_dir, 'cb_author_ids.npy'))
        
        try:
            author_work_counts = np.load(os.path.join(models_dir, 'cb_author_work_counts.npy'))
        except FileNotFoundError:
            author_work_counts = np.ones(len(author_ids), dtype=np.int32)
        
        # Cargar score priori
        try:
            author_prior = np.load(os.path.join(models_dir, 'cb_author_prior.npy'))
        except FileNotFoundError:
            author_prior = np.zeros(len(author_ids), dtype=np.float32)

        cls._cache = {
            'concept_to_index': concept_to_index,
            'author_matrix': author_matrix,
            'author_ids': author_ids,
            'author_work_counts': author_work_counts,
            'author_prior': author_prior,
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
        Bayesian smoothing por AUTOR:
        adjusted_score = (C * m_author + n * sim) / (C + n)

        Donde:
        - m: esperanza de similitud de todos los autores (es aprox 0)
        - n: cantidad de works del autor
        - sim: similitud cruda con el usuario
        - C: confianza
        """

        similarities = np.array(similarities, dtype=float)
        work_counts = np.array(work_counts, dtype=float)
        m = 0.0

        adjusted_scores = (
            confidence_param * m +
            work_counts * similarities
        ) / (confidence_param + work_counts)

        return adjusted_scores


    
    @classmethod
    def get_recommendations(cls, user_input):
        """
        Retorna TODOS los autores ordenados por similitud (sin threshold ni top_k),
        aplicando Bayesian smoothing con prior por concepto.
        
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
        
        # Calcular similitud coseno directamente
        similarities = cosine_similarity(user_vector, author_matrix)[0]
        
        # Aplicar Bayesian Smoothing usando score_prior
        similarities = cls.apply_bayesian_smoothing(
            similarities,
            author_work_counts,
            confidence_param=10.0
        )

        
        # Normalización Gaussiana (Z-score)
        mean = np.mean(similarities)
        std = np.std(similarities, ddof=0)
        
        if std == 0:
            similarities_norm = np.zeros_like(similarities)
        else:
            similarities_norm = (similarities - mean) / std
        
        # Ordenar autores por similitud descendente
        sorted_indices = np.argsort(-similarities_norm)
        sorted_author_ids = author_ids[sorted_indices]
        sorted_scores = similarities_norm[sorted_indices]
        
        # Empaquetar resultados
        recommendations = [
            (author_id, float(score))
            for author_id, score in zip(sorted_author_ids, sorted_scores)
        ]
        
        return recommendations
