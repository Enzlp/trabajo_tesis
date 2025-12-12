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
from recommender.collaborative_filtering.training_test import run_full_recommendation_system


#rating_matrix_file = rating_matrix(files_dir)

#matrix_factorization_als(
#     rating_matrix_file=rating_matrix_file,
#     files_dir=files_dir,
#     K=200,               # Alto K para capturar más relaciones sutiles
#     iterations=50,
#     alpha=50.0,
#     regularization=0.1, # Muy baja regularización para aumentar el Recall
#     num_threads=0
#)

# Hiperparametros 
#factors_list = [128, 200, 256]
#reg_list = [0.02, 0.05, 0.1, 0.2]
#iterations = 10  # mejor que 10

# Ejecutar grid search CORRECTO
#out = run_full_recommendation_system(
#    factors_list=factors_list,
#    reg_list=reg_list,
#    iterations=iterations,
#    K=20,
#    sample_users_eval=10000,
#    random_state=42,
#    save_dir=files_dir,
#    num_threads=0,
#    use_gpu=False
#)

#print(out)