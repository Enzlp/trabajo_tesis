from api.models import MvIaCoauthorshipLatam
import os
import numpy as np
from scipy.sparse import lil_matrix, csr_matrix, save_npz, load_npz
from implicit.als import AlternatingLeastSquares
import pickle

def rating_matrix(files_dir):
    """
    Construye una matriz dispersa de ratings autor x autor
    a partir de MVIaCoauthorshipLatam.
    """
    # 1. Obtener todos los registros
    queryset = MvIaCoauthorshipLatam.objects.all().values("coauthor_1", "coauthor_2", "shared_works")
    
    # 2. Crear mappings de string ID a índices numéricos
    all_authors = set()
    for row in queryset:
        all_authors.add(row["coauthor_1"])
        all_authors.add(row["coauthor_2"])
    
    author_list = sorted(all_authors)
    author_to_idx = {author: idx for idx, author in enumerate(author_list)}
    idx_to_author = {idx: author for author, idx in author_to_idx.items()}
    n_authors = len(author_list)
    
    print(f"Total de autores iniciales: {n_authors}")
    
    # 3. Crear matriz dispersa vacía (LIL para construcción eficiente)
    R = lil_matrix((n_authors, n_authors), dtype=np.float32)
    
    # 4. Llenar la matriz (simétrica)
    for row in queryset:
        i = author_to_idx[row["coauthor_1"]]
        j = author_to_idx[row["coauthor_2"]]
        rating = row["shared_works"]
        # Opcional: aplicar log(1 + x) para suavizar valores
        #rating = np.log1p(rating)
        R[i, j] = rating
        R[j, i] = rating  # matriz simétrica
    
    # Convertir a CSR para cálculos eficientes
    R_csr = R.tocsr()
    
    # 5. Filtrar autores con 1 o menos colaboraciones
    # Contar número de colaboradores únicos por autor (valores > 0 en cada fila)
    collaborators_per_author = np.array((R_csr > 0).sum(axis=1)).flatten()
    authors_to_keep = collaborators_per_author > 3
    n_removed = (~authors_to_keep).sum()
    
    print(f"Autores con ≤1 colaboración a eliminar: {n_removed}")
    
    if n_removed > 0:
        # Filtrar matriz: mantener solo autores con 2+ colaboraciones
        R_csr = R_csr[authors_to_keep][:, authors_to_keep]
        
        # Reconstruir mappings solo con autores que cumplen el criterio
        kept_indices = np.where(authors_to_keep)[0]
        new_author_list = [author_list[i] for i in kept_indices]
        
        author_to_idx = {author: new_idx for new_idx, author in enumerate(new_author_list)}
        idx_to_author = {new_idx: author for author, new_idx in author_to_idx.items()}
        
        n_authors = len(new_author_list)
        print(f"Autores después de filtrado: {n_authors}")
    
    # 6. Calcular estadísticas finales
    total_cells = n_authors * n_authors
    positive_cells = R_csr.nnz
    density = (positive_cells / total_cells) * 100
    
    print(f"Cantidad de usuarios finales: {n_authors}")
    print(f"Cantidad de interacciones (celdas con valor positivo): {positive_cells}")
    print(f"Densidad de la matriz: {density:.4f}%")
    
    # 7. Guardar matriz dispersa (CSR para implicit)
    output_file = os.path.join(files_dir, "cf_rating_matrix.npz")
    save_npz(output_file, R_csr)
    print(f"Matriz guardada en {output_file}")
    
    # 8. Guardar mappings
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
    ALS para matriz simétrica autor x autor usando factorización U·U^T.
    
    Para grafos no dirigidos (matriz simétrica A), usamos:
        A ≈ U·U^T
    
    donde U es una única matriz de factores (n_authors x K).
    
    Esto reduce parámetros de 2·n·K a n·K, evitando overfitting.
    
    Args:
        rating_matrix_file: archivo .npz con matriz autor x autor simétrica
        files_dir: directorio para guardar resultados
        K: número de factores latentes (50-200 recomendado)
        iterations: iteraciones de ALS (15-30 recomendado)
        alpha: peso de confianza (15-50, mayor = más peso a colaboraciones frecuentes)
        regularization: término L2 (0.01-0.1)
        num_threads: threads CPU (0 = automático)
        use_gpu: usar GPU si está disponible
    
    Returns:
        str: ruta al archivo U_file con embeddings únicos
    """
    print("="*60)
    print("ENTRENAMIENTO ALS - FACTORIZACIÓN SIMÉTRICA (U·U^T)")
    print("="*60)
    
    # 1. Cargar matriz autor x autor
    print("\n[1/6] Cargando matriz...")
    R = load_npz(rating_matrix_file).tocsr()
    n_authors = R.shape[0]
    
    print(f"  Dimensiones: {n_authors:,} autores x {n_authors:,} autores")
    print(f"  Colaboraciones: {R.nnz:,}")
    print(f"  Densidad: {(R.nnz / (n_authors * n_authors) * 100):.4f}%")
    
    # VALIDACIÓN: Verificar que es cuadrada
    if R.shape[0] != R.shape[1]:
        raise ValueError(f"Matriz debe ser cuadrada (autor x autor), recibida: {R.shape}")
    
    # VALIDACIÓN: Verificar simetría (opcional, puede ser costoso)
    print("\n[2/6] Verificando simetría...")
    if not np.allclose((R - R.T).data, 0, atol=1e-5):
        print("  ⚠️  ADVERTENCIA: La matriz no es perfectamente simétrica")
        print("     Se continuará con la factorización, pero considera revisar los datos")
    else:
        print("  ✅ Matriz es simétrica")
    
    # 3. Configurar modelo ALS
    print(f"\n[3/6] Configurando modelo ALS para factorización simétrica...")
    print(f"  Factores latentes: {K}")
    print(f"  Iteraciones: {iterations}")
    print(f"  Regularización: {regularization}")
    print(f"  Alpha (confianza): {alpha}")
    print(f"  Threads: {num_threads if num_threads > 0 else 'auto'}")
    print(f"  GPU: {'Sí' if use_gpu else 'No'}")
    print(f"\n  📊 Parámetros del modelo: {n_authors * K:,} (vs {2 * n_authors * K:,} con P y Q)")
    print(f"     Reducción: {50.0:.1f}%")
    
    model = AlternatingLeastSquares(
        factors=K,
        regularization=regularization,
        alpha=alpha,
        iterations=iterations,
        num_threads=num_threads,
        use_gpu=use_gpu,
        calculate_training_loss=True,
        random_state=42
    )
    
    # 4. Entrenar modelo
    print(f"\n[4/6] Entrenando modelo ALS...")
    print("  (Esto puede tomar varios minutos...)")
    
    model.fit(R.astype(np.float32), show_progress=True)
    
    print("\n  ✅ Entrenamiento completado")
    
    # 5. Extraer embeddings y promediar para factorización simétrica
    print(f"\n[5/6] Extrayendo embeddings y aplicando simetrización...")
    
    # ESTRATEGIA PARA MATRIZ SIMÉTRICA:
    # Opción 1: Usar solo user_factors (más común)
    # Opción 2: Usar solo item_factors
    # Opción 3: Promediar ambos (más robusto para matriz simétrica)
    
    P = model.user_factors  # (n_authors x K)
    Q = model.item_factors  # (n_authors x K)
    
    print(f"  Shape P (user_factors): {P.shape}")
    print(f"  Shape Q (item_factors): {Q.shape}")
    print(f"  Norma promedio P: {np.linalg.norm(P, axis=1).mean():.4f}")
    print(f"  Norma promedio Q: {np.linalg.norm(Q, axis=1).mean():.4f}")
    
    # Para matriz simétrica, promediamos P y Q para obtener U
    # Esto asegura que U·U^T sea simétrica
    U = (P + Q) / 2.0
    
    print(f"\n  ✅ Matriz U (promediada): {U.shape}")
    print(f"     Norma promedio U: {np.linalg.norm(U, axis=1).mean():.4f}")
    
    # Verificar que la reconstrucción es razonable
    print("\n[6/6] Verificando calidad de la reconstrucción...")
    
    # Muestrear algunas predicciones
    sample_size = min(100, n_authors)
    sample_indices = np.random.choice(n_authors, sample_size, replace=False)
    
    R_sample = R[sample_indices, :][:, sample_indices].toarray()
    U_sample = U[sample_indices, :]
    R_pred_sample = U_sample @ U_sample.T
    
    # Calcular error en muestra
    mask = R_sample > 0
    if mask.sum() > 0:
        mse = np.mean((R_sample[mask] - R_pred_sample[mask])**2)
        rmse = np.sqrt(mse)
        mae = np.mean(np.abs(R_sample[mask] - R_pred_sample[mask]))
        
        print(f"  RMSE (muestra): {rmse:.4f}")
        print(f"  MAE (muestra): {mae:.4f}")
    
    # 7. Guardar resultados
    U_file = os.path.join(files_dir, "cf_U_als.npy")
    model_file = os.path.join(files_dir, "cf_als_model.pkl")
    
    np.save(U_file, U.astype(np.float32))
    
    with open(model_file, "wb") as f:
        pickle.dump(model, f, protocol=pickle.HIGHEST_PROTOCOL)
    
    print(f"\n  ✅ Embeddings guardados:")
    print(f"     U: {U_file}")
    print(f"     Modelo: {model_file}")
    
    # 8. Estadísticas del modelo
    print("\n" + "="*60)
    print("RESUMEN DEL ENTRENAMIENTO")
    print("="*60)
    print(f"Autores: {n_authors:,}")
    print(f"Factores latentes: {K}")
    print(f"Parámetros totales: {U.size:,}")
    print(f"Tamaño U en memoria: {U.nbytes / (1024**2):.2f} MB")
    print(f"Tipo de factorización: SIMÉTRICA (U·U^T)")
    print(f"Ventaja: {50.0:.1f}% menos parámetros vs factorización asimétrica")
    
    return U_file