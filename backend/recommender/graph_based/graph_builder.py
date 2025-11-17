from api.models import LatamIaCoauthorshipView
import os
import gzip
import numpy as np
import pickle

"""
Se obtienen autores de latam con un tema de IA asociado y tengan colaboraciones
"""
def obtain_authors():
	author_ids_set = set()
	batch_size = 1000
	offset = 0
    		
	while True:
		batch = list(
			LatamIaCoauthorshipView.objects.values_list(
				"coauthor_1", "coauthor_2"
			)[offset:offset + batch_size]
		)
		if not batch:
			break
		
		for a, b in batch:
			author_ids_set.add(a)
			author_ids_set.add(b)

		offset += batch_size

	author_ids = sorted(list(author_ids_set))
	author_to_idx = {a: i for i, a in enumerate(author_ids)}

	return author_ids, author_to_idx


"""
Genera un archivo edgelist con la lista de todas las aristas del grafo y sus pesos
"""
def generate_edgelist(files_dir, author_ids, author_to_idx):
	output_path = os.path.join(files_dir, "coauthor_edges.edgelist.gz")
	os.makedirs(os.path.dirname(output_path), exist_ok=True)

	with gzip.open(output_path, "wt", encoding="utf-8") as f:
		batch_size = 10000
		offset = 0
		while True:
			coauthorships = list(
				LatamIaCoauthorshipView.objects.values_list(
					"coauthor_1", "coauthor_2", "shared_works"
				)[offset:offset + batch_size]
			)
			
			if not coauthorships:
				break
			
			for a, b, w in coauthorships:
				# Validar que los autores existan en el mapping
				if a not in author_to_idx or b not in author_to_idx:
					continue
				
				i = author_to_idx[a]
				j = author_to_idx[b]
				
				# Evitar self-loops
				if i == j:
					continue
				
				# Validar que el peso sea válido (no None, no negativo, no cero)
				if w is None or w <= 0:
					continue
				
				# Normalización logarítmica
				weight = np.log1p(w)
				
				# Validar que el peso sea finito (no NaN, no Inf)
				if not np.isfinite(weight):
					continue
				
				# Escribir edge (grafo no dirigido) con formato fijo
				f.write(f"{i} {j} {weight:.6f}\n")

			offset += batch_size
	
	# Guardar archivos generados
	mapping_path = os.path.join( os.path.dirname(output_path), "cf_author_mapping.pkl")
	with open(mapping_path, "wb") as p:
		# Solo guardamos la lista ordenada de IDs
		# El índice se puede reconstruir fácilmente
		pickle.dump({"author_ids": author_ids}, p)
