# training_test_symmetric_fixed.py
# Versión corregida: Train / Validation / Test + grid-search en validation +
# reentrenamiento final en Train+Val y evaluación en Test.


import os
import pickle
import time
import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix, vstack, save_npz, lil_matrix
from implicit.als import AlternatingLeastSquares
from api.models import MvIaCoauthorshipLatam


# -------------------------------
# 1) Cargar datos desde la BD y normalizar pares
# -------------------------------
def get_author_map_and_ratings(files_dir=None):
    """
    UNIFICA rating_matrix() y get_author_map_and_ratings().

    Hace TODO:
      - Carga coautorías
      - Genera author_list ordenado
      - Construye df_pairs_unique (para MF)
      - Construye matriz simétrica completa (para recomendaciones)
      - Guarda: 
            cf_rating_matrix.npz
            cf_author_to_idx.npy
            cf_idx_to_author.npy
      - Devuelve lo que usa MF:
            df_pairs_unique, author_to_idx, author_list
    """

    print("==============================================")
    print("📌 Cargando y construyendo datos CONSISTENTES para MF")
    print("==============================================\n")

    # 1) Cargar datos de la BD
    queryset = MvIaCoauthorshipLatam.objects.all().values(
        "coauthor_1", "coauthor_2", "shared_works"
    )

    all_authors = set()
    ratings_list = []

    for row in queryset:
        a = str(row["coauthor_1"])
        b = str(row["coauthor_2"])
        if a == b:
            continue

        all_authors.add(a)
        all_authors.add(b)

        ratings_list.append({
            "coauthor_1": a,
            "coauthor_2": b,
            "count": float(row["shared_works"]) if row["shared_works"] else 0.0
        })

    # 2) Ordenamiento lexicográfico — idéntico a MF
    author_list = sorted(all_authors)
    author_to_idx = {aid: i for i, aid in enumerate(author_list)}
    idx_to_author = {i: aid for i, aid in enumerate(author_list)}

    print(f"Autores únicos: {len(author_list):,}")

    # 3) Construir df_pairs_unique (para MF)
    df = pd.DataFrame(ratings_list)

    df["pair_min"] = df.apply(lambda r: r["coauthor_1"] if r["coauthor_1"] <= r["coauthor_2"] else r["coauthor_2"], axis=1)
    df["pair_max"] = df.apply(lambda r: r["coauthor_2"] if r["coauthor_1"] <= r["coauthor_2"] else r["coauthor_1"], axis=1)

    df_pairs_unique = df.drop_duplicates(subset=["pair_min", "pair_max"]).copy()
    df_pairs_unique["count"] = df_pairs_unique["count"].astype(float)
    df_pairs_unique = df_pairs_unique.reset_index(drop=True)

    print(f"Pares únicos: {len(df_pairs_unique):,}")

    # 4) Construir matriz simétrica autor x autor (para recomendación)
    n = len(author_list)
    R = lil_matrix((n, n), dtype=np.float32)

    for row in ratings_list:
        i = author_to_idx[row["coauthor_1"]]
        j = author_to_idx[row["coauthor_2"]]
        c = row["count"]

        R[i, j] = c
        R[j, i] = c

    R_csr = R.tocsr()

    # 5) Guardar si se requiere
    if files_dir is not None:
        os.makedirs(files_dir, exist_ok=True)

        matrix_file = os.path.join(files_dir, "cf_rating_matrix.npz")
        save_npz(matrix_file, R_csr)

        np.save(os.path.join(files_dir, "cf_author_to_idx.npy"), author_to_idx)
        np.save(os.path.join(files_dir, "cf_idx_to_author.npy"), idx_to_author)

        print("\n==============================================")
        print("✅ Datos guardados:")
        print(f"    Matriz: {matrix_file}")
        print(f"    author_to_idx.npy")
        print(f"    idx_to_author.npy")
        print("==============================================\n")

    return df_pairs_unique, author_to_idx, author_list

# -------------------------------
# 2) Train / Val / Test split por autor (LOO+Val seguro)
# -------------------------------
def train_val_test_split(df_pairs_unique, seed=42):
    """
    Divide en Train / Validation / Test por autor:
    - Autores con >=3 interacciones disponibles: 1 test, 1 val, resto train
    - Autores con 2 interacciones disponibles: 1 test, 1 train
    - Autores con 1 interacción: todo train

    IMPORTANTE: Un par (A,B) aparece en las listas de ambos autores.
    Usamos 'assigned' para evitar que el mismo par se asigne a múltiples conjuntos.

    Devuelve (df_train_unique, df_val_unique, df_test_unique)
    donde las filas son los pares únicos (pair_min/pair_max).
    """
    rng = np.random.default_rng(seed)

    # construir map author -> índices de fila (en df_pairs_unique)
    interactions = {}
    for idx, row in df_pairs_unique.iterrows():
        a = row["pair_min"]
        b = row["pair_max"]
        interactions.setdefault(a, []).append(idx)
        interactions.setdefault(b, []).append(idx)

    test_idx = set()
    val_idx = set()
    assigned = set()  # Rastrear pares ya asignados a test o val

    for author, idxs in interactions.items():
        # Filtrar índices que ya fueron asignados a test o val
        available = [i for i in idxs if i not in assigned]
        
        if len(available) >= 3:
            chosen_test = int(rng.choice(available))
            test_idx.add(chosen_test)
            assigned.add(chosen_test)

            available = [i for i in available if i != chosen_test]
            chosen_val = int(rng.choice(available))
            val_idx.add(chosen_val)
            assigned.add(chosen_val)

        elif len(available) == 2:
            chosen_test = int(rng.choice(available))
            test_idx.add(chosen_test)
            assigned.add(chosen_test)
        # si len(available) <= 1 -> todo train

    all_idx = set(df_pairs_unique.index)
    train_idx = all_idx - test_idx - val_idx

    df_train = df_pairs_unique.loc[sorted(list(train_idx))].copy().reset_index(drop=True)
    df_val = df_pairs_unique.loc[sorted(list(val_idx))].copy().reset_index(drop=True)
    df_test = df_pairs_unique.loc[sorted(list(test_idx))].copy().reset_index(drop=True)

    # Validar que no haya overlaps de PARES (índices de fila)
    overlap_test_val = len(test_idx.intersection(val_idx))
    overlap_train_test = len(train_idx.intersection(test_idx))
    overlap_train_val = len(train_idx.intersection(val_idx))
    
    assert overlap_test_val == 0, f"❌ Overlap entre Test y Val: {overlap_test_val}"
    assert overlap_train_test == 0, f"❌ Overlap entre Train y Test: {overlap_train_test}"
    assert overlap_train_val == 0, f"❌ Overlap entre Train y Val: {overlap_train_val}"
    print("✅ Sin overlaps de pares entre conjuntos (autores SÍ se comparten, como es esperado)")

    print(f"✔ Split sizes -> Train: {len(df_train):,} | Val: {len(df_val):,} | Test: {len(df_test):,}")
    return df_train, df_val, df_test

# -------------------------------
# 3) Construcción simétrica (explícita)
# -------------------------------
def build_symmetric(df_unique):
    """
    Construye DataFrame simétrico: agrega tanto (A,B) como (B,A).
    """
    df_sim1 = pd.DataFrame({
        "coauthor_1": df_unique["pair_min"].astype(str),
        "coauthor_2": df_unique["pair_max"].astype(str),
        "count": df_unique["count"].astype(float)
    })

    df_sim2 = pd.DataFrame({
        "coauthor_1": df_unique["pair_max"].astype(str),
        "coauthor_2": df_unique["pair_min"].astype(str),
        "count": df_unique["count"].astype(float)
    })

    return pd.concat([df_sim1, df_sim2], ignore_index=True)

# -------------------------------
# 4) Mapear a índices y construir sparse matrix
# -------------------------------
def map_indices_and_build(df_sym, author_to_idx):
    """
    Crea columnas coauthor_1_idx / coauthor_2_idx y retorna CSR matrix.
    Lanza ValueError si existen IDs en df_sym que no están en author_to_idx.
    """
    df_sym = df_sym.copy()  # CORRECCIÓN: evitar SettingWithCopyWarning
    df_sym["coauthor_1_idx"] = df_sym["coauthor_1"].map(author_to_idx)
    df_sym["coauthor_2_idx"] = df_sym["coauthor_2"].map(author_to_idx)

    n_missing = int(df_sym["coauthor_1_idx"].isna().sum()) + int(df_sym["coauthor_2_idx"].isna().sum())
    if n_missing > 0:
        print("❌ ERROR: existen IDs en df_sym que no están en author_to_idx:")
        print("  coauthor_1 missing:", df_sym["coauthor_1_idx"].isna().sum())
        print("  coauthor_2 missing:", df_sym["coauthor_2_idx"].isna().sum())
        raise ValueError("IDs inconsistentes entre datos y author_to_idx")

    rows = df_sym["coauthor_1_idx"].astype(int).values
    cols = df_sym["coauthor_2_idx"].astype(int).values
    data = df_sym["count"].astype(float).values

    n = len(author_to_idx)
    mat = csr_matrix((data, (rows, cols)), shape=(n, n), dtype=np.float32)
    return mat

# -------------------------------
# 5) Top-K from U (dot-product) — recomendación sin recommend()
# -------------------------------
def top_k_from_U(U, u, train_row, K):
    """
    Retorna los top-K items más similares según dot product,
    excluyendo los que ya están en train_row.
    """
    # scores vector
    scores = U @ U[u]

    # Excluir vistos
    seen = set(train_row.indices)
    if len(seen) > 0:
        scores[list(seen)] = -np.inf

    # evitar recomendar al mismo autor
    scores[u] = -np.inf

    n_items = scores.shape[0]
    K_eff = min(K, n_items)

    idx_part = np.argpartition(-scores, K_eff - 1)[:K_eff]
    topk = idx_part[np.argsort(-scores[idx_part])]

    return topk

# -------------------------------
# 6) Funciones Auxiliares para NDCG
# -------------------------------
def dcg_at_k(hits_gains, k):
    """Calcula el DCG para un usuario. hits_gains son las ganancias (relevancias) de los K ítems predichos."""
    hits_gains = np.asarray(hits_gains)[:k]
    # np.arange(2, len(hits_gains) + 2) genera [2, 3, 4, ...] para el denominador log2(i + 1)
    return np.sum(hits_gains / np.log2(np.arange(2, len(hits_gains) + 2)))

def ndcg_at_k_single(predicted_gains, gt_gains, k):
    """Calcula el NDCG para un único usuario."""
    # 1. Calcular DCG: de las ganancias de las predicciones
    dcg = dcg_at_k(predicted_gains, k)
    
    # 2. Calcular IDCG: usando las ganancias reales (ordenadas)
    # Se ordenan las ganancias reales de forma descendente para el IDCG
    ideal_gains = sorted(gt_gains, reverse=True)[:k]
    idcg = dcg_at_k(ideal_gains, k)
    
    # 3. NDCG = DCG / IDCG
    if idcg == 0.0:
        return 0.0
    return dcg / idcg

# -------------------------------
# 7) Evaluación Recall y NDCG (sustituye a recall_precision_at_k_sample_U)
# -------------------------------
def recall_ndcg_at_k_sample_U(U, R_train, R_target, users, K=10):
    """
    Calcula Recall@K y NDCG@K promediados.
    R_target usa los 'counts' como relevancia para NDCG.
    """
    recall_list = []
    ndcg_list = []
    evaluados = 0
    usuarios_sin_train = 0

    val_indptr = R_target.indptr
    val_indices = R_target.indices
    val_data = R_target.data

    for u in users:
        u = int(u)
        
        # 1. Verificar que el usuario tenga datos en R_train
        if R_train.getrow(u).nnz == 0:
            usuarios_sin_train += 1
            continue
            
        gt_indices = val_indices[val_indptr[u]:val_indptr[u+1]]
        gt_gains = val_data[val_indptr[u]:val_indptr[u+1]]
        
        if len(gt_indices) == 0:
            continue

        train_row = R_train.getrow(u)
        preds_indices = top_k_from_U(U, u, train_row, K)

        if len(preds_indices) == 0:
            continue
            
        # --- Cálculo de Recall ---
        hits = len(set(preds_indices).intersection(set(gt_indices)))
        recall_list.append(hits / len(gt_indices))
        
        # --- Cálculo de NDCG ---
        # 1. Crear mapa de GT a sus ganancias/relevancia
        gt_map = dict(zip(gt_indices, gt_gains))
        
        # 2. Obtener las ganancias de las K predicciones
        # Ganancia es 'count' si acierta, 0.0 si no.
        predicted_gains = [gt_map.get(idx, 0.0) for idx in preds_indices]

        # 3. Calcular NDCG
        ndcg = ndcg_at_k_single(predicted_gains, gt_gains, K)
        ndcg_list.append(ndcg)
        
        evaluados += 1

    if usuarios_sin_train > 0:
        print(f"  ⚠️  {usuarios_sin_train} usuarios sin interacciones en R_train (omitidos)")

    if evaluados == 0:
        return 0.0, 0.0, 0 # recall, ndcg, evaluados

    return float(np.mean(recall_list)), float(np.mean(ndcg_list)), evaluados

# -------------------------------
# 8) Entrenamiento ALS y simetrización (sin cambios)
# -------------------------------
def train_als_symmetric(R_train, factors=64, reg=0.01, iterations=15, num_threads=0, use_gpu=False):
    """
    Entrena ALS (implicit) y retorna embeddings simétricos U = (P + Q) / 2
    """
    R_train = R_train.tocsr().astype(np.float32)

    model = AlternatingLeastSquares(
        factors=factors,
        regularization=reg,
        iterations=iterations,
        num_threads=num_threads,
        use_gpu=use_gpu,
        calculate_training_loss=False,
        random_state=42
    )

    # implicit.fit espera item_users (items x users)
    item_users = R_train.T
    model.fit(item_users)

    P = model.user_factors
    Q = model.item_factors

    U = (P + Q) / 2.0
    return U.astype(np.float32), model

# -------------------------------
# 9) Pipeline principal (Train/Val/Test) - MODIFICADO
# -------------------------------
def run_full_recommendation_system(
    factors_list=[64, 128],
    reg_list=[0.01, 0.1],
    iterations=10,
    K=10,
    sample_users_eval=10000,
    random_state=42,
    save_dir=None,
    num_threads=0,
    use_gpu=False
):
    """
    Pipeline:
      - carga datos
      - split train/val/test por autor
      - construye matrices simétricas R_train, R_val, R_test
      - grid-search: entrena en R_train y evalúa en R_val (Usando Recall y NDCG)
      - re-entrena en R_train+R_val con mejores hiperparámetros (basado en NDCG)
      - evalúa en R_test
    """
    print("============================================================")
    print("🚀 SISTEMA DE RECOMENDACIÓN - ALS SIMÉTRICO (Train/Val/Test)")
    print("============================================================")

    # 1) Carga
    df_pairs_unique, author_to_idx, author_list = get_author_map_and_ratings(save_dir)

    # 2) split train/val/test
    df_train_unique, df_val_unique, df_test_unique = train_val_test_split(df_pairs_unique, seed=random_state)

    # 3) construir simétricos
    print("\n📊 Construyendo matrices simétricas...")
    df_train_sym = build_symmetric(df_train_unique)
    df_val_sym = build_symmetric(df_val_unique)
    df_test_sym = build_symmetric(df_test_unique)

    # 4) mapear y construir sparse
    print("🔧 Mapeando a índices y construyendo sparse matrices...")
    R_train = map_indices_and_build(df_train_sym, author_to_idx)
    R_val = map_indices_and_build(df_val_sym, author_to_idx)
    R_test = map_indices_and_build(df_test_sym, author_to_idx)

    R_train = R_train.tocsr().astype(np.float32)
    R_val = R_val.tocsr().astype(np.float32)
    R_test = R_test.tocsr().astype(np.float32)

    print(f"✔ R_train: {R_train.shape}, nnz={R_train.nnz:,}, dtype={R_train.dtype}")
    print(f"✔ R_val: {R_val.shape}, nnz={R_val.nnz:,}, dtype={R_val.dtype}")
    print(f"✔ R_test: {R_test.shape}, nnz={R_test.nnz:,}, dtype={R_test.dtype}")
    
    train_users_count = np.sum(R_train.getnnz(axis=1) > 0)
    val_users_count = np.sum(R_val.getnnz(axis=1) > 0)
    test_users_count = np.sum(R_test.getnnz(axis=1) > 0)
    
    print(f"\n🔎 Usuarios con interacciones:")
    print(f"  Train: {train_users_count:,} usuarios")
    print(f"  Val: {val_users_count:,} usuarios")
    print(f"  Test: {test_users_count:,} usuarios")

    # 5) Elegir muestra de usuarios
    rng = np.random.default_rng(random_state)
    valid_train_users = np.where(R_train.getnnz(axis=1) > 0)[0]
    n_sample = min(sample_users_eval, len(valid_train_users))
    sample_users = rng.choice(valid_train_users, size=n_sample, replace=False)
    print(f"✔ Sample users para evaluación: {len(sample_users):,}")

    # 6) grid search (evalúa en VAL)
    print("\n" + "="*60)
    print("🔍 GRID SEARCH - Evaluación en VALIDATION")
    print("="*60)
    
    results = []
    best_score = -1.0
    best_model = None
    best_params = None

    for f in factors_list:
        for r in reg_list:
            print(f"\n🔧 Probando: factors={f}, regularization={r}, iterations={iterations}")
            t0 = time.time()

            U, model = train_als_symmetric(R_train, factors=f, reg=r, iterations=iterations, num_threads=num_threads, use_gpu=use_gpu)
            train_time = time.time() - t0

            # --- USO DE LA NUEVA FUNCIÓN ---
            rc_val, ndcg_val, n_eval = recall_ndcg_at_k_sample_U(U, R_train, R_val, sample_users, K=K)

            results.append({
                "factors": f,
                "regularization": r,
                "iterations": iterations,
                "Recall@K_val": rc_val,
                "NDCG@K_val": ndcg_val, # MODIFICADO
                "Evaluados_val": n_eval,
                "Train_Sec": train_time
            })

            print(f"  → VAL Recall@{K}: {rc_val:.6f} | VAL NDCG@{K}: {ndcg_val:.6f} | Evaluados: {n_eval} | Train: {train_time:.2f}s") # MODIFICADO

            # --- SELECCIÓN DEL MEJOR MODELO POR NDCG ---
            if ndcg_val > best_score:
                best_score = ndcg_val # Ahora el mejor score es el NDCG
                best_model = (U, model)
                best_params = {"factors": f, "regularization": r, "iterations": iterations, "Recall@K_val": rc_val, "NDCG@K_val": ndcg_val} # MODIFICADO

    # 7) re-entrenar en Train + Val con mejores hiperparámetros
    if best_params is None:
        raise RuntimeError("No se encontró mejor configuración durante la validación.")

    print("\n" + "="*60)
    print("🏆 MEJOR CONFIGURACIÓN EN VALIDATION (Por NDCG):") # MODIFICADO
    for k, v in best_params.items():
        print(f"  {k}: {v}")
    print("="*60)
    print("\n🔄 Re-entrenando en Train+Val con esos hiperparámetros...")

    # Construir R_train_plus_val
    R_train_plus_val = (R_train + R_val).tocsr()
    print(f"✔ R_train_plus_val: {R_train_plus_val.shape}, nnz={R_train_plus_val.nnz:,}")

    f_best = best_params["factors"]
    r_best = best_params["regularization"]
    #it_best = best_params["iterations"]

    t0 = time.time()
    U_final, model_final = train_als_symmetric(R_train_plus_val, factors=f_best, reg=r_best, iterations=50, num_threads=num_threads, use_gpu=use_gpu)
    train_time_final = time.time() - t0
    print(f"✔ Re-entrenamiento final completado en {train_time_final:.2f}s")

    # 8) Actualizar sample_users para TEST
    valid_trainval_users = np.where(R_train_plus_val.getnnz(axis=1) > 0)[0]
    n_sample_test = min(sample_users_eval, len(valid_trainval_users))
    sample_users_test = rng.choice(valid_trainval_users, size=n_sample_test, replace=False)
    print(f"✔ Sample users para TEST: {len(sample_users_test):,}")

    # 9) Evaluación final en TEST
    print("\n" + "="*60)
    print("📊 EVALUACIÓN FINAL EN TEST")
    print("="*60)
    # --- USO DE LA NUEVA FUNCIÓN EN TEST ---
    rc_test, ndcg_test, n_eval_test = recall_ndcg_at_k_sample_U(U_final, R_train_plus_val, R_test, sample_users_test, K=K)
    print(f"\n→ TEST Recall@{K}: {rc_test:.6f}")
    print(f"→ TEST NDCG@{K}: {ndcg_test:.6f}") # MODIFICADO
    print(f"→ Usuarios evaluados: {n_eval_test:,}")

    # 10) Guardar resultados y modelo
    if save_dir is not None:
        os.makedirs(save_dir, exist_ok=True)

        # Mantener nombres compatibles con matrix_factorization_als()
        U_file = os.path.join(save_dir, "cf_U_als.npy")
        model_file = os.path.join(save_dir, "cf_als_model.pkl")

        # Guardar U final (entrenado con Train+Validation)
        np.save(U_file, U_final.astype(np.float32))

        # Guardar modelo ALS final
        with open(model_file, "wb") as f:
            pickle.dump(model_final, f, protocol=pickle.HIGHEST_PROTOCOL)

        print(f"\n✅ Embeddings guardados en: {U_file}")
        print(f"✅ Modelo guardado en: {model_file}")

    # Construir DataFrame ordenado por VAL (usando NDCG)
    df_results = pd.DataFrame(results).sort_values(
        ["NDCG@K_val", "Recall@K_val"], # MODIFICADO
        ascending=False
    ).reset_index(drop=True)

    summary = {
        "best_params_val": best_params,
        "val_results_df": df_results,
        "test_metrics": {
            "Recall@K": rc_test,
            "NDCG@K": ndcg_test, # MODIFICADO
            "Evaluados": n_eval_test
        },
        #"U_file": U_file if save_dir else None,
        #"model_file": model_file if save_dir else None,
        #"U_final": U_final,
        #"model_final": model_final,
        #"author_list": author_list,
        #"author_to_idx": author_to_idx
    }

    return summary

# -------------------------------
# End of file
# -------------------------------