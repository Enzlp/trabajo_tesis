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
        # Esto da la fila author_idx de la matriz reconstruida U·U^T
        predicted_scores = U[author_idx] @ U.T
        
        # Excluir al mismo autor (guardamos el valor original para no afectar la normalización)
        original_self_score = predicted_scores[author_idx]
        predicted_scores[author_idx] = -np.inf
        
        # Normalización Gaussiana (Z-Score)
        # Importante: excluir -np.inf del cálculo de estadísticas
        valid_scores = predicted_scores[predicted_scores != -np.inf]
        
        mean = np.mean(valid_scores)
        std = np.std(valid_scores, ddof=0)  # ddof=0 para corrección de muestra
        
        # Manejar caso donde std = 0 (todos los valores iguales)
        if std == 0:
            predicted_scores_norm = np.where(
                predicted_scores == -np.inf,
                -np.inf,
                0.0
            )
        else:
            predicted_scores_norm = np.where(
                predicted_scores == -np.inf,
                -np.inf,
                (predicted_scores - mean) / std
            )
        
        # Ordenar todos los autores por score normalizado (mayor a menor)
        sorted_indices = np.argsort(-predicted_scores_norm)
        
        # Construir toda la lista de recomendaciones
        recommendations = [
            (idx_to_author[idx], float(predicted_scores_norm[idx]))
            for idx in sorted_indices
            if predicted_scores_norm[idx] != -np.inf  # Excluir el autor mismo
        ]
        
        return recommendations
    
