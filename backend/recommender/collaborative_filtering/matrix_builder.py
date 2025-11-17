from api.models import LatamIaCoauthorshipView
import os
import numpy as np
from scipy.sparse import lil_matrix, csr_matrix, save_npz, load_npz
from implicit.als import AlternatingLeastSquares
import pickle

def rating_matrix(files_dir):
    """
    Construye una matriz dispersa de ratings autor x autor
    a partir de LatamIaCoauthorshipView.
    """

    # 1. Obtener todos los registros
    queryset = LatamIaCoauthorshipView.objects.all().values("coauthor_1", "coauthor_2", "shared_works")

    # 2. Crear mappings de string ID a índices numéricos
    all_authors = set()
    for row in queryset:
        all_authors.add(row["coauthor_1"])
        all_authors.add(row["coauthor_2"])

    author_list = sorted(all_authors)
    author_to_idx = {author: idx for idx, author in enumerate(author_list)}
    idx_to_author = {idx: author for author, idx in author_to_idx.items()}

    n_authors = len(author_list)
    print(f"Total de autores: {n_authors}")

    # 3. Crear matriz dispersa vacía (LIL para construcción eficiente)
    R = lil_matrix((n_authors, n_authors), dtype=np.float32)

    # 4. Llenar la matriz
    for row in queryset:
        i = author_to_idx[row["coauthor_1"]]
        j = author_to_idx[row["coauthor_2"]]
        rating = row["shared_works"]

        # Opcional: aplicar log(1 + x) para suavizar valores
        #rating = np.log1p(rating)

        R[i, j] = rating
        R[j, i] = rating  # si quieres la matriz simétrica

    # 5. Guardar matriz dispersa (CSR para implicit)
    output_file = os.path.join(files_dir, "cf_rating_matrix.npz")
    save_npz(output_file, R.tocsr())
    print(f"Matriz guardada en {output_file}")

    # 6. Guardar mappings
    np.save(os.path.join(files_dir, "cf_author_to_idx.npy"), author_to_idx)
    np.save(os.path.join(files_dir, "cf_idx_to_author.npy"), idx_to_author)

    return output_file


def matrix_factorization_implicit(rating_matrix_file, files_dir, K=20, iterations=15, 
                                   regularization=0.01, use_gpu=False, num_threads=0):
    """
    Factoriza la matriz R en P y Q usando ALS (Alternating Least Squares) con implicit.
    
    IMPORTANTE: implicit también usa Matrix Factorization, solo que con ALS en vez de SGD.
    El resultado es el mismo: R ≈ P @ Q^T
    
    Args:
        rating_matrix_file: ruta al archivo .npz con la matriz de ratings
        files_dir: directorio para guardar P y Q
        K: número de características latentes (factors en implicit)
        iterations: número de iteraciones de ALS (equivalente a epochs en SGD)
        regularization: parámetro de regularización (equivalente a beta en SGD)
        use_gpu: si True, usa GPU (requiere CUDA y implicit[gpu])
        num_threads: número de threads (0 = auto, usa todos los cores disponibles)
    
    Returns:
        Tuplas con rutas a P y Q
    """
    # Cargar matriz dispersa
    R = load_npz(rating_matrix_file)
    n_users, n_items = R.shape
    
    print(f"Iniciando factorización con implicit (ALS): {n_users} usuarios, {n_items} ítems, {K} factores latentes")
    print(f"Elementos no-cero: {R.nnz} ({100*R.nnz/(n_users*n_items):.4f}% de densidad)")
    print(f"GPU: {use_gpu}, Threads: {num_threads if num_threads > 0 else 'auto'}")
    
    # Crear modelo ALS
    model = AlternatingLeastSquares(
        factors=K,
        regularization=regularization,
        iterations=iterations,
        use_native=True,      # Usa código C++ optimizado
        use_cg=True,          # Usa Conjugate Gradient (más rápido)
        use_gpu=use_gpu,
        num_threads=num_threads,
        calculate_training_loss=True  # Para monitorear convergencia
    )
    
    # Entrenar (fit espera formato item_users, así que transponemos)
    # implicit espera matriz user x item, tu matriz es autor x autor (simétrica)
    print("Entrenando modelo...")
    model.fit(R)
    
    # Extraer matrices P y Q
    P = model.user_factors   # n_users x K
    Q = model.item_factors   # n_items x K
    
    # Guardar P y Q como archivos NumPy (más simple que HDF5 para matrices pequeñas)
    P_file = os.path.join(files_dir, "cf_P_matrix.npy")
    Q_file = os.path.join(files_dir, "cf_Q_matrix.npy")
    
    np.save(P_file, P)
    np.save(Q_file, Q)
    
    print(f"Factorización completada.")
    print(f"P guardada en: {P_file} (shape: {P.shape})")
    print(f"Q guardada en: {Q_file} (shape: {Q.shape})")
    
    # Opcional: guardar el modelo completo para usar métodos de implicit
    model_file = os.path.join(files_dir, "cf_implicit_model.pkl")
    with open(model_file, 'wb') as f:
        pickle.dump(model, f)
    print(f"Modelo completo guardado en: {model_file}")
    
    return P_file, Q_file







