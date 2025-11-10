import os
import numpy as np
import pickle

class CollaborativeFilteringQueries:
    """
    Método para cargar modelos
    """
    @staticmethod
    def load_models(models_dir):
        emb = np.load(os.path.join(models_dir, "cf_author_embeddings.npy"))
        with open(os.path.join(models_dir, "cf_author_mapping.pkl"), "rb") as f:
            mapping = pickle.load(f)
            
        author_ids = mapping["author_ids"]
        author_to_idx = {author_id: idx for idx, author_id in enumerate(author_ids)}
        
        norms = np.linalg.norm(emb, axis=1, keepdims=True)
        norms = np.where(norms == 0, 1e-10, norms)
        emb_norm = emb / norms
        return emb_norm, author_to_idx, author_ids
    
    """
    Metodo para obtener recomendaciones usando el modelo entrenado de node2vec
    """
    @classmethod
    def get_recommendations(cls, author_id, k = 20):

        models_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "files")
        print(models_dir)
        emb_norm, author_to_idx, author_ids = cls.load_models(models_dir)
        if author_id not in author_to_idx:
            return []
        
        idx = author_to_idx[author_id]

        # Verificar que el embedding no sea cero
        if np.allclose(emb_norm[idx], 0):
            print(f"⚠️  Warning: El autor {author_id} tiene embedding cero")
            return []
        
        # Vector del autor query
        query_vec = emb_norm[idx]

        # Calcular cosine similarity con todos los autores (dot product de vectores normalizados)
        similarities = np.dot(emb_norm, query_vec)
        
        # Obtener los k+1 más similares (incluye al mismo autor)
        top_indices = np.argsort(similarities)[::-1][:k+1]
        
        # Construir resultados
        results = []
        for node_idx in top_indices:
            if node_idx == idx:  # Saltar el mismo autor
                continue
            
            real_author_id = author_ids[node_idx]
            similarity = float(similarities[node_idx])
            results.append((real_author_id, similarity))
        
        return results[:k]
        