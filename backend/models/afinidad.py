from pyalex import Authors, Subfields
import numpy as np

# =========================================================
# Modelo de recomendaciones de investigadores afines en IA
# =========================================================


# Obtencion de datos por API

# Códigos de paises de LATAM
latam_countries = ['AR', 'BO', 'BR', 'CL', 'CO', 'CR', 'CU', 'DO', 'EC', 'SV', 'GT', 'HN', 'MX', 'NI', 'PA', 'PY', 'PE', 'PR', 'UY', 'VE']
latam_countries_str = "|".join(latam_countries)

# Codigos de topicos dentro subfield IA
topic_ids = [t['id'].split('/')[-1] for t in Subfields().filter(id=1702).get(per_page=200)[0]['topics']]
topics_str = "|".join(topic_ids)

# Autores en IA y LATAM paginados
authors_paginated = Authors().filter(
    **{
        "last_known_institutions.country_code": latam_countries_str,
        "topics.id": topics_str
    }
).paginate(method="page", per_page=200)

# Obtencion de datos para cada autor
author_data = []
count = 0
max_authors = 100000  

for page in authors_paginated:
    if not page or count >= max_authors:
        break
    author_data.extend(page)
    count += len(page)

# Id para autores
author_ids = [a['id'].split('/')[-1] for a in author_data]

# Generamos la matriz de pesos para similitud
n = len(author_ids)
m = len(topic_ids)

weight_matrix = np.zeros((n, m))
topic_index = {t_id: j for j, t_id in enumerate(topic_ids)}

for i, a in enumerate(author_data):
    for t in a.get('topics', []):
        t_id = t['id'].split('/')[-1]
        if t_id in topic_index:
            j = topic_index[t_id]
            weight_matrix[i][j] = 1


# Me da la direccion del vector de topicos interes, es decir hacia donde va el interes del investigador. Similitud entre vectores
def similarity(x, y):
    norm_x = np.linalg.norm(x)
    norm_y = np.linalg.norm(y)
    if norm_x == 0 or norm_y == 0:
        return 0
    return np.dot(x, y) / (norm_x * norm_y)


#### Ejemplos ####
# usamos un vector de topicos dado por el usuario, donde cada topico pedido es un 1
user_input = np.ones(m)

# Calculamos similitudes
sim_scores = np.array([similarity(vec, user_input) for vec in weight_matrix])

# Obtenemos índices de los 20 autores con mayor similitud
top_idx = np.argsort(sim_scores)[-20:][::-1]  
top_20_author_idx = top_idx.tolist()


# Imprimimos resultados
print("Top 20 autores más afines a los tópicos:")
for idx in top_idx:
    print(f"Autor {author_ids[idx]} - Similitud: {sim_scores[idx]:.4f}")
