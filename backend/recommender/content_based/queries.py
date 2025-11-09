import os
import pickle
import joblib
import numpy as np
from scipy.sparse import lil_matrix
from sklearn.metrics.pairwise import cosine_similarity

class ContentBasedQueries:

	"""
	Metodo para cargar modelos precalculados
	"""
	@staticmethod
	def load_models(models_dir):
		# Mapeo de conceptos
		with open(os.path.join(models_dir, 'concept_mapping.pkl'), 'rb') as f:
				concept_to_index = pickle.load(f)

		# Modelo SVD
		svd_model = joblib.load(os.path.join(models_dir , 'svd_model.pkl'))

		# Modelo embeddings autor
		author_embeddings = np.load(os.path.join(models_dir , 'cb_author_embeddings.npy'))

		# IDs de autores
		author_ids = np.load(os.path.join(models_dir , 'cb_author_ids.npy'))

		return concept_to_index, svd_model, author_embeddings, author_ids
	

	"""
	Metodo para crear el vector de conceptos del usuario
	"""
	@staticmethod
	def create_user_vector(user_concepts, n_concepts, concepts_ids):
		user_vector = lil_matrix((1, n_concepts), dtype=np.float32)
		smoothing = 0.12
		user_vector[:] = smoothing  # valor minimo para conceptos = 0

		for concept in user_concepts:
			concept_id = concept['id']
			concept_idx = concepts_ids[concept_id]
			user_vector[0, concept_idx] = 1.0  # valor maximo conceptos seleccionados

		user_vector = user_vector.tocsr()

		return user_vector

	"""
	Metodo para obtener el listado de recomendaciones basados en el vector de conceptos de usuario ingresado
	"""
	@classmethod
	def get_recommendations(cls, user_input, top_k = 20, similarity_threshold=0.2):
		# Cargar modelos
		models_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "files")
		concept_to_index, svd_model, author_embeddings, author_ids = cls.load_models(models_dir)
		n_concepts = len(concept_to_index)

		# Crear vector de usuario
		user_vector = cls.create_user_vector(user_input, n_concepts, concept_to_index)

		# Crear embeddings de usuario
		user_embedding = svd_model.transform(user_vector.toarray())

		# Calcular similitudes
		similarities = cosine_similarity(user_embedding, author_embeddings)[0]

		# filtrar autores por umbral
		filtered_indices = np.where(similarities >= similarity_threshold)[0]
		if len(filtered_indices) == 0:
			return []  # No hay autores sobre el umbral
		
		# Obtener top_k sobre el umbral
		top_indices = filtered_indices[np.argsort(similarities[filtered_indices])[-top_k:][::-1]]

		# Obtener IDs de autores
		top_author_ids = author_ids[top_indices].tolist()

		recommendations = []
		for idx, author_id in zip(top_indices, top_author_ids):
			recommendations.append((author_id, float(similarities[idx])))


		return recommendations

