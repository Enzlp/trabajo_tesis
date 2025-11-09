import os
import pickle
from api.models import MvLatamIaConceptView
import numpy as np
from scipy.sparse import lil_matrix
from sklearn.preprocessing import normalize
from sklearn.decomposition import TruncatedSVD
import joblib

"""
Entrena SVD para reducir dimensionalidad de la matriz dispersa generada de conceptos para cada autor
"""
def train_svd(files_dir):
    # Mapeo de conceptos
	concept_mapping_path = os.path.join(files_dir, "concept_mapping.pkl")
	with open(concept_mapping_path, 'rb') as f:
		concept_to_index = pickle.load(f)
	n_concepts = len(concept_to_index)

	# Cargar autores
	authors_data = list(MvLatamIaConceptView.objects.all().order_by('author_id'))
	n_authors = len(authors_data)

	# Matriz dispersa
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

	# Normalizacion
	matrix = normalize(matrix, norm='l2', axis=1)

	# Aplicar SVD a la matriz dispersa
	svd = TruncatedSVD(n_components=100, random_state=42)
	embeddings = svd.fit_transform(matrix)

	# Guardar archivos generados
	joblib.dump(svd, os.path.join(files_dir, 'svd_model.pkl'))
	np.save(os.path.join(files_dir, 'cb_author_embeddings.npy'), embeddings.astype(np.float32))
	np.save(os.path.join(files_dir, 'cb_author_ids.npy'), np.array(author_ids))
