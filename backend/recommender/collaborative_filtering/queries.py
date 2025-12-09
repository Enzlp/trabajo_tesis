# Contenido de recommender/collaborative_filtering/queries.py (Modificado)

import numpy as np
import os


class CollaborativeFilteringQueries:
    # Cache estático a nivel de clase
    _cache = None
    
    @classmethod
    def _initialize_cache(cls):
        """Inicializa el cache una sola vez"""
        if cls._cache is not None:
            return
        
        files_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
            "files"
        )
        
        # Cargar todo una sola vez
        cls._cache = {
            'author_to_idx': np.load(
                os.path.join(files_dir, "cf_author_to_idx.npy"), 
                allow_pickle=True
            ).item(),
            'idx_to_author': np.load(
                os.path.join(files_dir, "cf_idx_to_author.npy"), 
                allow_pickle=True
            ).item(),
            'U': np.load(os.path.join(files_dir, "cf_U_als.npy"))
        }

    @classmethod
    def get_recommendations(cls, author_id):
        # Inicializar cache si es necesario
        cls._initialize_cache()
        
        # Usar datos del cache
        author_to_idx = cls._cache['author_to_idx']
        idx_to_author = cls._cache['idx_to_author']
        U = cls._cache['U']
        
        if author_id not in author_to_idx:
            print(f"Autor {author_id} no encontrado")
            return []
        
        author_idx = author_to_idx[author_id]
        
        # Calcular scores: U[author_idx] @ U^T
        predicted_scores = U[author_idx] @ U.T
        
        # Excluir al mismo autor
        predicted_scores[author_idx] = -np.inf
        
        valid_scores = predicted_scores[predicted_scores != -np.inf]
        
        epsilon = 1e-8    

        # 🔹 Normalización Min-Max (Score de Fusión)
        min_score = predicted_scores[predicted_scores != -np.inf].min()
        max_score = predicted_scores.max()

        
        if (max_score - min_score) > epsilon:
            # Solo normalizamos los scores válidos, manteniendo -np.inf
            predicted_scores_norm = np.where(
                predicted_scores == -np.inf,
                -np.inf,
                (predicted_scores - min_score) / (max_score - min_score)
            )
        else:
            predicted_scores_norm = np.where(
                predicted_scores == -np.inf,
                -np.inf,
                np.zeros_like(predicted_scores)
            )

        #K_SCALER = 0.5
        #valid_scores = predicted_scores[predicted_scores != -np.inf]
        #center_point = np.median(valid_scores)
        #predicted_scores_centered = predicted_scores - center_point
        #predicted_scores_norm = np.where(
        #predicted_scores == -np.inf,
        #    -np.inf,
        #    1.0 / (1.0 + np.exp(-K_SCALER * predicted_scores_centered))
        #)
        
        # Ordenar todos los autores por score normalizado min-max (mayor a menor)
        sorted_indices = np.argsort(-predicted_scores_norm)
        
        # Construir toda la lista de recomendaciones: (author_id, score_min_max, z_score)
        recommendations = [
            (idx_to_author[idx], float(predicted_scores_norm[idx]))
            for idx in sorted_indices
            if predicted_scores_norm[idx] != -np.inf # Excluir el autor mismo
        ]
        
        return recommendations
