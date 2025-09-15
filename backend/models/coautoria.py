# =======================================================================
# Modelo de Collaborative Filtering para redes de coautoría
# =======================================================================

# Si un investigador A colabora con los mismos investigadores que investigador B, entonces es muy probable que el resto de investigadores
# con los que colabore B tambien le gusten a A

# El rating será el numero de papers entre invesitgador A y C. Se normalizan los valores por frecuencia total. El enfoque de frecuencia ayuda a que se evidencie
# la fuerza de relacion entre autores, entre mas colaboraciones entre dos autores sobre el total, mas fuerte es la relacion entre esos dos autores.

from pyalex import Works, Authors
from scipy.sparse import coo_matrix, csr_matrix # matriz dispersa
from collections import Counter
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import heapq

# Hay un total de 139391 autores en IA y LATAM. Esto nos daría una matriz de 139391 x 139391 lo que es muy grande para RAM, por lo que deberiamos usar
# una matriz dispersa. 

# Podemos ver la red de colaboracion como un grafo, donde el investigador target hace "rating" de los investigadores de primer nivel (contacto directo), 
# es decir la cantidad de papers en conjunto. Luego los investigadores de segundo nivel tambien hacen "rating" a los de primer nivel, por lo que son los
# que pueden ser mas similar, ahi se calcula simlitud. Con los investigadores mas similares se obtienen las recomendaciones. 

# PENDIENTE: Filtrar por LATAM y opcionalmente por IA

# ------- Parametros -------
# Obtenemos los datos de coautoría para un autor ej: Andres Abeliuk
target_author = 'A5038897083'

# --- Coautores de nivel 1 ---
works_target_author = Works().filter(
    **{"authorships.author.id": target_author}
).get(per_page=200)

target_counts = Counter()
for work in works_target_author:
    for auth in work["authorships"]:
        author_id = auth["author"]["id"].split("/")[-1]
        if author_id != target_author:
            target_counts[author_id] += 1

level1_authors = list(target_counts.keys())


# --- Coautores de nivel 2 ---

rows = []
cols = []
data = []

author_index = {target_author: 0}  # índice único para cada autor
current_index = 1

# Agregar colaboraciones del target
for coauthor_id, count in target_counts.items():
    if coauthor_id not in author_index:
        author_index[coauthor_id] = current_index
        current_index += 1
    rows.append(author_index[target_author])
    cols.append(author_index[coauthor_id])
    data.append(count)

# Obtener coautores de nivel 2
for coauthor in level1_authors:
    works_coauthor = Works().filter(
        **{"authorships.author.id": coauthor}
    ).get(per_page=200)

    coauthor_counts = Counter()
    for work in works_coauthor:
        for auth in work['authorships']:
            coauth_id = auth['author']['id'].split("/")[-1]
            if coauth_id != target_author and coauth_id != coauthor:
                coauthor_counts[coauth_id] += 1

    # Agregar estos coautores a la matriz
    for coauth_id, count in coauthor_counts.items():
        if coauth_id not in author_index:
            author_index[coauth_id] = current_index
            current_index += 1
        rows.append(author_index[coauthor])
        cols.append(author_index[coauth_id])
        data.append(count)

# Crear matriz dispersa
n_authors = len(author_index)
sparse_matrix = coo_matrix((data, (rows, cols)), shape=(n_authors, n_authors))
sparse_csr = sparse_matrix.tocsr()

print(f"Número de autores en la matriz (target + niveles 1 y 2): {n_authors}")
print(f"Matriz dispersa creada con forma: {sparse_matrix.shape}")

# --- Creamos matriz de similtud ---
# Encontramos los vecinos mas similares al autor

target_idx = author_index[target_author]
target_vector = sparse_csr[target_idx]

# Cosine similarity entre target y todos los autores
similarities = cosine_similarity(target_vector, sparse_csr)[0]
similarities[target_idx] = -1  # excluir el propio target

# Obtener índices de los top autores
top_indices = np.argsort(similarities)[::-1][:10] # marca la cantidad de autores similares
top_scores = similarities[top_indices]

# Mapear índices a IDs de OpenAlex
inv_author_index = {v: k for k, v in author_index.items()}
top_authors = [inv_author_index[i] for i in top_indices]

# Resultado final: lista de tuplas (author_id, score)
top_similar_authors = list(zip(top_authors, top_scores))

# ---- Generar recomendaciones ----

latam_countries = ['AR', 'BO', 'BR', 'CL', 'CO', 'CR', 'CU', 'DO', 'EC', 'SV', 'GT', 'HN', 'MX', 'NI', 'PA', 'PY', 'PE', 'PR', 'UY', 'VE']

# Función de score
def score(weight, sim):
    return weight * sim

# Función para verificar si un autor está en LATAM
def is_latam(author_id):
    author_data = Authors()[author_id]
    if 'last_known_institutions' in author_data:
        for institution in author_data['last_known_institutions']:
            country_code = institution.get('country_code')
            if country_code and country_code in latam_countries:
                return True
    return False

recommended_authors = {}  # autor_id -> score acumulado

for neighbor_author, sim in top_similar_authors:
    works_recommended = Works().filter(
        **{"authorships.author.id": neighbor_author}
    ).get()
    
    for work in works_recommended:
        for auth in work["authorships"]:
            author_id = auth["author"]["id"].split("/")[-1]
            
            # Ignorar target y vecinos directos
            if author_id == target_author or author_id == neighbor_author:
                continue
            
            # Filtrar autores LATAM
            if not is_latam(author_id):
                continue
            
            # Sumar score: peso = 1 por cada paper compartido
            s = score(weight=1, sim=sim)
            if author_id in recommended_authors:
                recommended_authors[author_id] += s
            else:
                recommended_authors[author_id] = s


top_recommended = heapq.nlargest(20, recommended_authors.items(), key=lambda x: x[1])

# Resultado: lista de tuplas (autor_id, score)
print(top_recommended)
