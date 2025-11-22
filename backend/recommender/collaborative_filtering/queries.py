import numpy as np
import os
from scipy.sparse import load_npz
import h5py
import pickle


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
            'P': np.load(os.path.join(files_dir, "cf_P_als.npy")),
            'Q': np.load(os.path.join(files_dir, "cf_Q_als.npy"))
        }
    
    @classmethod
    def get_recommendations(cls, author_id, top_n=10):
        # Inicializar cache si es necesario
        cls._initialize_cache()
        
        # Usar datos del cache
        author_to_idx = cls._cache['author_to_idx']
        idx_to_author = cls._cache['idx_to_author']
        P = cls._cache['P']
        Q = cls._cache['Q']
        
        if author_id not in author_to_idx:
            print(f"Autor {author_id} no encontrado")
            return []
        
        author_idx = author_to_idx[author_id]
        
        # Calcular scores (usar @ en lugar de np.dot)
        predicted_scores = P[author_idx] @ Q.T
        
        # Excluir al mismo autor
        predicted_scores[author_idx] = -np.inf
        
        # Top-K eficiente con argpartition O(n) en lugar de sort O(n log n)
        k = min(top_n, len(predicted_scores) - 1)
        top_indices = np.argpartition(-predicted_scores, k-1)[:k]
        top_indices = top_indices[np.argsort(-predicted_scores[top_indices])]
        
        # Construir resultados (solo k conversiones, no 370k)
        top_recs = [
            (idx_to_author[idx], float(predicted_scores[idx]))
            for idx in top_indices
        ]
        
        return top_recs
