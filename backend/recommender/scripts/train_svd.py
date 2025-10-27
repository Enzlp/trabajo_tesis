# ==============================================================================
# Entrena modelo SVD para reducir matriz a menor dimensiones y guarda la matriz
# ==============================================================================

import sys
import os
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
import django
django.setup()

from api.models import MvLatamIaConceptView
import pickle
from scipy.sparse import lil_matrix
import numpy as np
from sklearn.preprocessing import normalize
from sklearn.decomposition import TruncatedSVD
import joblib

# Inicia Script
print("Iniciando entrenamiento SVD...")

# 1. Cargar Mapeo de conceptos
concept_mapping_path = Path("recommender/files/concept_mapping.pkl")
with open(concept_mapping_path, 'rb') as f:
    concept_to_index = pickle.load(f)
n_concepts = len(concept_to_index)

# 2. Cargar autores
authors_data = list(MvLatamIaConceptView.objects.all().order_by('author_id'))
n_authors = len(authors_data)

# 3. Construcción matriz sparse
matrix = lil_matrix((n_authors, n_concepts), dtype=np.float32)
author_ids = []

for author_idx, author in enumerate(authors_data):
    author_ids.append(author.author_id)
    
    concept_ids = author.concept_ids or []
    concept_scores = author.concept_scores or []
    
    for i, concept_id in enumerate(concept_ids):
        if concept_id not in concept_to_index:
            continue
        concept_idx = concept_to_index[concept_id]
        score = float(concept_scores[i]) if i < len(concept_scores) else 1.0
        matrix[author_idx, concept_idx] = score

matrix = matrix.tocsr()

# 4. Normalización (row-wise L2)
matrix = normalize(matrix, norm='l2', axis=1)

# 5. Entrenar Truncated SVD (equivalente a PCA para sparse)
svd = TruncatedSVD(n_components=100, random_state=42)
embeddings = svd.fit_transform(matrix)

# 6. Guardar archivos
files_dir = Path('recommender/files')
files_dir.mkdir(exist_ok=True, parents=True)

# Guardar modelo SVD
joblib.dump(svd, files_dir / 'svd_model.pkl')

# Guardar embeddings y author_ids usando NumPy
np.save(files_dir / 'author_embeddings.npy', embeddings.astype(np.float32))
np.save(files_dir / 'author_ids.npy', np.array(author_ids))

print(f"Completado. Embeddings guardados para {n_authors} autores con {embeddings.shape[1]} dimensiones.")
