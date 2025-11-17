import numpy as np
import os
from scipy.sparse import load_npz
import h5py
import pickle


class CollaborativeFilteringQueries:
	@classmethod
	def get_recommendations(cls, author_id, top_n=10):
		"""
		Obtiene recomendaciones para un autor sin incluir al mismo autor.
		"""
		files_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "files")

		# Cargar mappings
		author_to_idx = np.load(os.path.join(files_dir, "cf_author_to_idx.npy"), 
														allow_pickle=True).item()
		idx_to_author = np.load(os.path.join(files_dir, "cf_idx_to_author.npy"), 
														allow_pickle=True).item()
		
		if author_id not in author_to_idx:
				print(f"Autor {author_id} no encontrado")
				return []
		
		author_idx = author_to_idx[author_id]
		
		# Cargar modelo y matriz original
		with open(os.path.join(files_dir, "cf_implicit_model.pkl"), 'rb') as f:
				model = pickle.load(f)
		
		R_original = load_npz(os.path.join(files_dir, "cf_rating_matrix.npz"))
		
		# Obtener recomendaciones
		indices, scores = model.recommend(
				author_idx, 
				R_original[author_idx],
				N=top_n + 5,   # pedimos más por si hay que filtrar
				filter_already_liked_items=True
		)
		
		# Convertimos a (author_id, score)
		recs = [
				(idx_to_author[int(idx)], float(score))
				for idx, score in zip(indices, scores)
		]
		
		# Filtrar: remover el mismo autor si aparece
		recs = [r for r in recs if r[0] != author_id]
		
		# --- MIN-MAX sobre los scores CF ---
		score_vals = [s for _, s in recs]
		min_s, max_s = min(score_vals), max(score_vals)

		if max_s - min_s < 1e-9:
			# todos iguales → asignar 1.0 a todos
			recs_norm = [(aid, 1.0) for aid, _ in recs]
		else:
			recs_norm = [
				(aid, (s - min_s) / (max_s - min_s))
				for aid, s in recs
			]

		# devolver top_n con scores normalizados
		return recs_norm[:top_n]