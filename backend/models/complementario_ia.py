# ==============================================================================================
# Modelo basado en contenido para encontrar investigadores complementarios (en IA)
# ==============================================================================================

# ============================================================
# Complementaridad entre tópicos
# C(i,j) = coocurrencias(i,j) / (ocurrencias(i) + ocurrencias(j))
# ============================================================

from pyalex import Subfields, Authors
import numpy as np
import pandas as pd
import math

df = pd.read_csv("cooc_matrix_ia.csv", index_col=0)
occurrences = df.sum(axis=1)
C = pd.DataFrame(index=df.index, columns=df.columns, dtype=float)

for i in df.index:
    for j in df.columns:
        denom = occurrences[i] + occurrences[j]
        if denom > 0:
            C.loc[i, j] = df.loc[i, j] / denom
        else:
            C.loc[i, j] = 0

latam_countries = ['AR','BO','BR','CL','CO','CR','CU','DO','EC','SV',
                   'GT','HN','MX','NI','PA','PY','PE','PR','UY','VE']
latam_countries_str = "|".join(latam_countries)
total_recommendations = 20
m = len(df)

# Ejemplo de entrada del usuario: todos los tópicos activos
user_input = np.zeros(m)
user_input[30] = 1
user_input[2] = 1

topics_ia = [t['id'].split('/')[-1] for t in Subfields().filter(id=1702).get(per_page=200)[0]['topics']]
selected_topics = [topics_ia[i] for i, v in enumerate(user_input) if v == 1 and i < len(topics_ia)]
selected_vectors = C.loc[selected_topics]
user_vector = selected_vectors.mean(axis=0)
user_vector = user_vector / user_vector.sum()
topics_recommended = user_vector * total_recommendations

# Filtrar y mostrar solo los tópicos con valores > 0
topics_mayores_cero = topics_recommended[topics_recommended >= 1].sort_values(ascending=False).astype(int)

# Multiplicamos hasta obtener el numero de recomendaciones que queremos
k = (total_recommendations/topics_mayores_cero.sum()).round(0)
topics_mayores_cero = topics_mayores_cero*k

authors_rec = []
for topic_id, value in topics_mayores_cero.items():    
    authors = Authors().filter(
        **{
            "last_known_institutions.country_code": latam_countries_str,
            "topics.id": topic_id
        }
    ).sort(works_count="desc").get(per_page=int(value))
    x = [a['id'].split('/')[-1] for a in authors]
    authors_rec.extend(x)

authors_rec = authors_rec[:total_recommendations]
print(authors_rec)