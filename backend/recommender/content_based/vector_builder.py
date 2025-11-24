import os
from api.models import MvIaConceptView
import pickle
from api.models import MvLatamIaConceptView
import numpy as np
from scipy.sparse import lil_matrix, save_npz
from sklearn.preprocessing import normalize

"""
Crea un archivo con el mapeo de conceptos a indices
"""
def map_concepts(files_dir):
	concepts = MvIaConceptView.objects.values_list("id", flat=True).order_by("id")
	concept_mapping = {concept_id: idx for idx, concept_id in enumerate(concepts)}
	file_path = os.path.join(files_dir, 'concept_mapping.pkl')
	with open(file_path, "wb") as f:
		pickle.dump(concept_mapping, f, protocol=pickle.HIGHEST_PROTOCOL)

def train_model(files_dir):
    # Cargar mapping de conceptos
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
    author_work_counts = []

    print(f"Procesando {n_authors} autores con {n_concepts} conceptos...")

    # Para calcular score priori
    concept_scores_accum = [[] for _ in range(n_concepts)]  # lista de listas

    for author_idx, author in enumerate(authors_data):
        author_ids.append(author.author_id)
        
        concept_ids = author.concept_ids or []
        concept_scores = author.concept_scores or []
        
        # Obtener cantidad de works
        work_count = getattr(author, 'works_count', len(concept_ids))
        author_work_counts.append(work_count)
        
        for i, concept_id in enumerate(concept_ids):
            if concept_id not in concept_to_index:
                continue
            concept_idx = concept_to_index[concept_id]
            score = float(concept_scores[i]) if i < len(concept_scores) else 1.0
            matrix[author_idx, concept_idx] = score
            
            # Acumular score para prior solo si existe
            concept_scores_accum[concept_idx].append(score)
        
        if (author_idx + 1) % 1000 == 0:
            print(f"  Procesados {author_idx + 1}/{n_authors} autores...")

    # Convertir a CSR (más eficiente)
    matrix = matrix.tocsr()
    # Normalización L2 por filas
    matrix = normalize(matrix, norm='l2', axis=1)

    # Guardar matriz y metadata
    save_npz(os.path.join(files_dir, 'author_concept_matrix.npz'), matrix)
    np.save(os.path.join(files_dir, 'cb_author_ids.npy'), np.array(author_ids))
    np.save(os.path.join(files_dir, 'cb_author_work_counts.npy'), np.array(author_work_counts))



    # Estadísticas
    work_counts_array = np.array(author_work_counts)
    metadata = {
        'n_concepts': n_concepts,
        'n_authors': n_authors,
        'mean_works': float(np.mean(work_counts_array)),
        'median_works': float(np.median(work_counts_array)),
        'min_works': int(np.min(work_counts_array)),
        'max_works': int(np.max(work_counts_array)),
        'sparsity': float(matrix.nnz / (n_authors * n_concepts))
    }
    
    with open(os.path.join(files_dir, 'model_metadata.pkl'), 'wb') as f:
        pickle.dump(metadata, f, protocol=pickle.HIGHEST_PROTOCOL)
    
    print("\n=== Entrenamiento completado ===")
    print(f"Total autores: {n_authors}")
    print(f"Total conceptos: {n_concepts}")
    print(f"Promedio works/autor: {metadata['mean_works']:.2f}")
    print(f"Mediana works/autor: {metadata['median_works']:.2f}")
    print(f"Rango works: {metadata['min_works']} - {metadata['max_works']}")
    print(f"Sparsity: {metadata['sparsity']*100:.2f}%")
    print(f"Tamaño matriz: {matrix.data.nbytes / (1024**2):.2f} MB")