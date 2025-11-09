import sys 
import os

# Establece raiz del proyecto como path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")

import django
django.setup()

# Generamos los archivos para cada modelo de recomendacion
from recommender.content_based.vector_builder import map_concepts
from recommender.content_based.trainer import train_svd
from recommender.collaborative_filtering.graph_builder import obtain_authors, generate_edgelist
from recommender.collaborative_filtering.trainer import train_node2vec

# directorio de archivos
files_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "files")

# Archivo de mapeo de conceptos
map_concepts(files_dir)

# Reducir dimensionalidad SVD
train_svd(files_dir)

# Obtener autores
author_ids, author_to_idx = obtain_authors()

# Generar edgelist
generate_edgelist(files_dir, author_ids, author_to_idx)

# Entrenar node2vec
train_node2vec(files_dir)

# Limpieza de archivos
os.remove(os.path.join(files_dir, "coauthor_edges.edgelist"))
os.remove(os.path.join(files_dir, "coauthor_edges.edgelist.gz"))