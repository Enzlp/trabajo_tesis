from recommender.content_based.queries import ContentBasedQueries
from recommender.collaborative_filtering.queries import CollaborativeFilteringQueries

class HybridRecommender:
    @staticmethod
    def get_recommendations(user_input=None, author_id=None, k=30, alpha=0.5, beta=0.5, order_by='sim', country_code=''):

        content = ContentBasedQueries()
        colab = CollaborativeFilteringQueries()

        # Solo content-based
        if user_input and not author_id:
            recs = content.get_recommendations(user_input=user_input)  # <-- sin top_k
            return recs[:k]

        # Solo colab-based
        if author_id and not user_input:
            recs = colab.get_recommendations(author_id=author_id)  # <-- sin top_n
            return recs[:k]

        # Nada llega
        if not user_input and not author_id:
            return []

        # HÍBRIDO CORRECTO -----------------------------------------
        recs_1 = content.get_recommendations(user_input=user_input)     
        recs_2 = colab.get_recommendations(author_id=author_id)          

        if len(recs_2) == 0:
            return recs_1[:k]

        d1 = {aid: score for aid, score in recs_1}
        d2 = {aid: score for aid, score in recs_2}

        all_authors = set(d1.keys()) | set(d2.keys())

        fused = []
        for aid in all_authors:
            s1 = d1.get(aid, 0.1)
            s2 = d2.get(aid, 0.1)
            final_score = alpha * s1 + beta * s2
            fused.append((aid, final_score))

        fused.sort(key=lambda x: x[1], reverse=True)
        return fused[:k]



