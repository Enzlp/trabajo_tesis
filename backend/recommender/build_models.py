import sys 
import os

# Establece raiz del proyecto como path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")

import django
django.setup()

# Generamos los archivos para cada modelo de recomendacion
from recommender.content_based.vector_builder import map_concepts, train_model

# directorio de archivos
files_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "files")

# Archivo de mapeo de conceptos
map_concepts(files_dir)

train_model(files_dir)


# GRAPH


#authors_to_idx = obtain_authors_lightgcn()
#generate_edgelist_lightgcn(files_dir, authors_to_idx)


#edge_path = os.path.join(files_dir, "coauthor_edges.edgelist")

#train_lightgcn_pyg(edge_path)

from recommender.collaborative_filtering.matrix_builder import rating_matrix,  matrix_factorization_als

rating_matrix_file = rating_matrix(files_dir)

P_file, Q_file = matrix_factorization_als(
    rating_matrix_file=rating_matrix_file,
    files_dir=files_dir,
    K=250,                # tamaño grande para capturar estructura en grafo
    iterations=50,        # suficiente para convergencia estable
    alpha=20.0,           # peso moderado (colaboraciones repetidas valen más)
    regularization=0.05,  # regularización más fuerte por alta dispersión
    num_threads=0
)




