from api.models import LatamIaCoauthorshipView
import os
import numpy as np
from scipy.sparse import lil_matrix, csr_matrix, save_npz, load_npz
from implicit.als import AlternatingLeastSquares
from implicit.bpr import BayesianPersonalizedRanking
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


def matrix_factorization_als(
    rating_matrix_file, 
    files_dir, 
    K=50, 
    iterations=20,
    alpha=40.0, 
    regularization=0.01, 
    num_threads=0,
    use_gpu=False
):
    """
    ALS implícito (Hu, Koren, Volinsky 2008) para matriz autor x autor.
    
    Modelo:
    - p_ij = 1 si r_ij > 0 (hay colaboración)
    - p_ij = 0 si r_ij = 0 (información faltante, NO negativo)
    - c_ij = 1 + alpha * r_ij (confianza)
    
    Optimiza: SUM c_ij * (p_ij - u_i^T v_j)^2 + regularización
    
    Args:
        rating_matrix_file: archivo .npz con matriz autor x autor
        files_dir: directorio para guardar resultados
        K: número de factores latentes (50-200 recomendado)
        iterations: iteraciones de ALS (15-30 recomendado)
        alpha: peso de confianza (15-50, mayor = más peso a colaboraciones frecuentes)
        regularization: término L2 (0.01-0.1)
        num_threads: threads CPU (0 = automático)
        use_gpu: usar GPU si está disponible
    
    Returns:
        tuple: (P_file, Q_file) con embeddings de autores
    """
    print("="*60)
    print("ENTRENAMIENTO ALS - FEEDBACK IMPLÍCITO")
    print("="*60)
    
    # 1. Cargar matriz autor x autor
    print("\n[1/5] Cargando matriz...")
    R = load_npz(rating_matrix_file).tocsr()
    n_authors = R.shape[0]
    n_items = R.shape[1]
    
    print(f"  Dimensiones: {n_authors:,} autores x {n_items:,} autores")
    print(f"  Colaboraciones: {R.nnz:,}")
    print(f"  Densidad: {(R.nnz / (n_authors * n_items) * 100):.4f}%")
    
    # VALIDACIÓN: Verificar que es cuadrada y simétrica
    if n_authors != n_items:
        raise ValueError(f"Matriz debe ser cuadrada (autor x autor), recibida: {R.shape}")
    
    # 2. Preparar matriz de confianza
    print(f"\n[2/5] Aplicando ponderación de confianza (alpha={alpha})...")
    
    # IMPORTANTE: NO transponer porque ya es autor x autor simétrica
    # implicit espera (items x users), pero en nuestro caso items=users=autores
    C = R.copy()
    
    # Aplicar transformación de confianza: c_ij = 1 + alpha * r_ij
    # NOTA: No modificamos el .data directamente en C, dejamos que ALS lo haga
    # implicit.als internamente aplica la transformación si usamos alpha
    
    print(f"  Valores únicos en matriz original: {np.unique(R.data)[:10]}")
    print(f"  Min colaboraciones: {R.data.min()}, Max: {R.data.max()}")
    
    # 3. Configurar modelo ALS
    print(f"\n[3/5] Configurando modelo ALS...")
    print(f"  Factores latentes: {K}")
    print(f"  Iteraciones: {iterations}")
    print(f"  Regularización: {regularization}")
    print(f"  Alpha (confianza): {alpha}")
    print(f"  Threads: {num_threads if num_threads > 0 else 'auto'}")
    print(f"  GPU: {'Sí' if use_gpu else 'No'}")
    
    model = AlternatingLeastSquares(
        factors=K,
        regularization=regularization,
        alpha=alpha,  # CRÍTICO: pasar alpha al modelo
        iterations=iterations,
        num_threads=num_threads,
        use_gpu=use_gpu,
        calculate_training_loss=True,
        random_state=42
    )
    
    # 4. Entrenar modelo
    print(f"\n[4/5] Entrenando modelo ALS...")
    print("  (Esto puede tomar varios minutos...)")
    
    # IMPORTANTE: Pasar la matriz original (autor x autor)
    # implicit.als maneja internamente la confianza con alpha
    model.fit(C.astype(np.float32), show_progress=True)
    
    print("\n  ✅ Entrenamiento completado")
    
    # 5. Extraer embeddings
    print(f"\n[5/5] Extrayendo y guardando embeddings...")
    
    # CRÍTICO: Como NO transponemos, los factores están correctamente asignados
    # - user_factors = embeddings de autores (filas de la matriz)
    # - item_factors = embeddings de autores (columnas, pero en matriz simétrica son iguales)
    
    # Para matriz simétrica autor x autor:
    # Podemos usar user_factors O item_factors (deberían ser similares)
    # Usamos user_factors como representación principal
    
    P = model.user_factors  # Embeddings de autores (n_authors x K)
    
    # Para matriz simétrica, item_factors también representa autores
    Q = model.item_factors  # También embeddings de autores (n_authors x K)
    
    print(f"  Shape P (user_factors): {P.shape}")
    print(f"  Shape Q (item_factors): {Q.shape}")
    
    # Verificar que los embeddings son razonables
    print(f"  Norma promedio P: {np.linalg.norm(P, axis=1).mean():.4f}")
    print(f"  Norma promedio Q: {np.linalg.norm(Q, axis=1).mean():.4f}")
    
    # 6. Guardar resultados
    P_file = os.path.join(files_dir, "cf_P_als.npy")
    Q_file = os.path.join(files_dir, "cf_Q_als.npy")
    model_file = os.path.join(files_dir, "cf_als_model.pkl")
    
    np.save(P_file, P.astype(np.float32))
    np.save(Q_file, Q.astype(np.float32))
    
    with open(model_file, "wb") as f:
        pickle.dump(model, f, protocol=pickle.HIGHEST_PROTOCOL)
    
    print(f"\n  ✅ Embeddings guardados:")
    print(f"     P: {P_file}")
    print(f"     Q: {Q_file}")
    print(f"     Modelo: {model_file}")
    
    # 7. Estadísticas del modelo
    print("\n" + "="*60)
    print("RESUMEN DEL ENTRENAMIENTO")
    print("="*60)
    print(f"Autores: {n_authors:,}")
    print(f"Factores latentes: {K}")
    print(f"Parámetros totales: {(P.size + Q.size):,}")
    print(f"Tamaño P en memoria: {P.nbytes / (1024**2):.2f} MB")
    print(f"Tamaño Q en memoria: {Q.nbytes / (1024**2):.2f} MB")
    
    return P_file, Q_file
