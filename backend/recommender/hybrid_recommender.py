from recommender.content_based.queries import ContentBasedQueries
from recommender.graph_based.queries import GraphBasedQueries
from recommender.collaborative_filtering.queries import CollaborativeFilteringQueries

class HybridRecommender:
    @staticmethod
    def get_recommendations(user_input=None, author_id=None, k=30, alpha= 0.5, beta=0.5):

        content = ContentBasedQueries()
        graph = GraphBasedQueries()
        colab = CollaborativeFilteringQueries()

        # ------------------------------------------------------------------
        # 1. Manejo de casos incompletos
        # ------------------------------------------------------------------

        # Solo content-based
        if user_input and not author_id:
            return content.get_recommendations(user_input=user_input, top_k=k)
        

        # Solo graph based
        if author_id and not user_input:
            return colab.get_recommendations(author_id=author_id, top_n=k)

        # Si no llega nada
        if not user_input and not author_id:
            return []

        # ------------------------------------------------------------------
        # 2. Ambos disponibles: fusion híbrida
        # ------------------------------------------------------------------
        recs_1 = content.get_recommendations(user_input=user_input, top_k=k)
        recs_2 = colab.get_recommendations(author_id=author_id, top_n=k)

        # Si el autor no tiene colaboraciones en el grafo usa content based
        if len(recs_2) == 0:
            return recs_1

        d1 = {aid: score for aid, score in recs_1}
        d2 = {aid: score for aid, score in recs_2}

        # Unión de todos los autores recomendados por ambos sistemas
        all_authors = set(d1.keys()) | set(d2.keys())

        fused = []
        for aid in all_authors:
            s1 = d1.get(aid, 0.1)
            s2 = d2.get(aid, 0.1)
            final_score = alpha * s1 + beta * s2
            fused.append((aid, final_score))

        fused.sort(key=lambda x: x[1], reverse=True)
        return fused[:k]



