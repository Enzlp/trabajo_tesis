# ==============================================================================================
# Modelo basado en contenido para encontrar investigadores complementarios (interdisciplinarios)
# ==============================================================================================

from pyalex import Subfields, Authors
import numpy as np
import pandas as pd



# Normalizamos la matriz usando División por la suma de la fila
df = pd.read_csv("cooc_matrix.csv", index_col=0)
df_normalized = df.div(df.sum(axis=1), axis=0)

def score(cooc_value, num_papers):
  return cooc_value*num_papers

# ------------ Caso Práctico ---------------

latam_countries = ['AR', 'BO', 'BR', 'CL', 'CO', 'CR', 'CU', 'DO', 'EC', 'SV', 'GT', 'HN', 'MX', 'NI', 'PA', 'PY', 'PE', 'PR', 'UY', 'VE']
latam_countries_str = "|".join(latam_countries)


m = 77
user_input = np.ones(m)

topics_ia = [t['id'].split('/')[-1] for t in Subfields().filter(id=1702).get(per_page=200)[0]['topics']]

selected_topics = [topics_ia[i] for i, v in enumerate(user_input) if v == 1]

selected_vectors = df_normalized.loc[selected_topics]

user_vector = selected_vectors.mean(axis=0)

topic_comp = user_vector.idxmax()

authors_rec = Authors().filter(
    **{
        "last_known_institutions.country_code": latam_countries_str,
        "topics.id": topic_comp
    }
).sort(works_count="desc").get()

recommendations = [a['id'].split('/')[-1] for a in authors_rec]

print(recommendations)