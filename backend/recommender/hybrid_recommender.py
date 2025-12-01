# Contenido de recommender/hybrid_recommender.py (Modificado)

from recommender.content_based.queries import ContentBasedQueries
from recommender.collaborative_filtering.queries import CollaborativeFilteringQueries

class HybridRecommender:
    @staticmethod
    def get_recommendations(user_input=None, author_id=None, k=30, alpha=0.5, beta=0.5, order_by='sim', country_code=''):

        content = ContentBasedQueries()
        colab = CollaborativeFilteringQueries()

        # Solo content-based (Devuelve 3, se añade 4to elemento para consistencia)
        if user_input and not author_id:
            recs = content.get_recommendations(user_input=user_input)  
            recs_padded = [(aid, mm_score, z_score_cb, 0.0) for aid, mm_score, z_score_cb in recs]
            return recs_padded[:k]

        # Solo colab-based (Devuelve 3, se añade 4to elemento para consistencia)
        if author_id and not user_input:
            recs = colab.get_recommendations(author_id=author_id)  
            recs_padded = [(aid, mm_score, 0.0, z_score_colab) for aid, mm_score, z_score_colab in recs]
            return recs_padded[:k]

        # Nada llega
        if not user_input and not author_id:
            return []

        # HÍBRIDO CORRECTO -----------------------------------------
        # Ambos recs devuelven: (aid, mm_score, z_score)
        recs_1 = content.get_recommendations(user_input=user_input)     
        recs_2 = colab.get_recommendations(author_id=author_id)          

        if len(recs_2) == 0:
            recs_padded = [(aid, mm_score, z_score_cb, 0.0) for aid, mm_score, z_score_cb in recs_1]
            return recs_padded[:k]

        # d1 y d2 almacenan (mm_score, z_score)
        d1 = {aid: (score_mm, z_score) for aid, score_mm, z_score in recs_1}
        d2 = {aid: (score_mm, z_score) for aid, score_mm, z_score in recs_2}

        all_authors = set(d1.keys()) | set(d2.keys())

        fused = []
        for aid in all_authors:
            # Obtener scores y Z-scores de ambos modelos (usando 0.0 como default)
            s1_mm, s1_z = d1.get(aid, (0.0, 0.0)) # Content-Based
            s2_mm, s2_z = d2.get(aid, (0.0, 0.0)) # Collaborative Filtering

            # Suma Ponderada (Weighted Sum) con scores Min-Max
            final_score = alpha * s1_mm + beta * s2_mm
            
            # Salida: (author_id, final_hybrid_score, z_score_cb, z_score_colab)
            fused.append((aid, final_score, s1_z, s2_z)) 

        fused.sort(key=lambda x: x[1], reverse=True)
        return fused[:k]