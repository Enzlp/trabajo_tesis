# training_test_symmetric.py
# Entrenamiento ALS adaptado a matriz autor x autor (simétrica)
# Produce embeddings U tal que A ≈ U · U^T y evalúa Recall@K con LOO seguro.

import os
import pickle
import time
import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
from implicit.als import AlternatingLeastSquares
from api.models import LatamIaCoauthorshipView

# -------------------------------
# 1) Cargar datos desde la BD y normalizar pares
# -------------------------------
def get_author_map_and_ratings():
    """
    Carga coautorías desde la BD y construye pares únicos (pair_min, pair_max).

    Returns:
        df_pairs_unique: DataFrame con columnas [pair_min, pair_max, count]
        author_to_idx: dict mapping author_id (str) -> int
        author_list: lista ordenada de author_id (str)
    """
    print("📥 Cargando datos de coautoría desde la base de datos...")
    t0 = time.time()

    queryset = LatamIaCoauthorshipView.objects.all().values(
        "coauthor_1", "coauthor_2", "shared_works"
    )

    all_authors = set()
    ratings_list = []

    for row in queryset:
        a = str(row["coauthor_1"])
        b = str(row["coauthor_2"])

        # ignorar self-loops
        if a == b:
            continue

        all_authors.add(a)
        all_authors.add(b)

        ratings_list.append({
            "coauthor_1": a,
            "coauthor_2": b,
            "count": float(row["shared_works"]) if row["shared_works"] is not None else 0.0
        })

    # Normalizar set de autores a strings y ordenar
    author_list = sorted({str(x) for x in all_authors})
    author_to_idx = {aid: i for i, aid in enumerate(author_list)}

    # DataFrame con todos los pares (dirección original)
    df = pd.DataFrame(ratings_list)

    # Asegurar columnas string
    df["coauthor_1"] = df["coauthor_1"].astype(str)
    df["coauthor_2"] = df["coauthor_2"].astype(str)

    # Construir pair_min / pair_max de forma explícita (strings)
    df["pair_min"] = df.apply(lambda r: r["coauthor_1"] if r["coauthor_1"] <= r["coauthor_2"] else r["coauthor_2"], axis=1)
    df["pair_max"] = df.apply(lambda r: r["coauthor_2"] if r["coauthor_1"] <= r["coauthor_2"] else r["coauthor_1"], axis=1)

    # Quitar duplicados por par único
    df_pairs_unique = df.drop_duplicates(subset=["pair_min", "pair_max"]).copy()
    df_pairs_unique = df_pairs_unique.reset_index(drop=True)

    # Asegurar tipos y columna count
    df_pairs_unique["pair_min"] = df_pairs_unique["pair_min"].astype(str)
    df_pairs_unique["pair_max"] = df_pairs_unique["pair_max"].astype(str)
    df_pairs_unique["count"] = df_pairs_unique["count"].astype(float)

    elapsed = time.time() - t0
    print(f"🔹 Pares únicos: {len(df_pairs_unique):,}")
    print(f"🔹 Autores únicos: {len(author_list):,}")
    print(f"⏱️ Tiempo carga datos: {elapsed:.2f}s")

    return df_pairs_unique, author_to_idx, author_list

# -------------------------------
# 2) Leave-One-Out por autor (safe)
# -------------------------------
def leave_one_out_split(df_pairs_unique, seed=42):
    """
    Leave-One-Out SEGURO:
    - Para cada autor con >=2 interacciones → se deja 1 en test.
    - Para autores con 1 interacción → se quedan 100% en train.
    """
    rng = np.random.default_rng(seed)
    interactions = {}

    for idx, row in df_pairs_unique.iterrows():
        a = row["pair_min"]
        b = row["pair_max"]
        interactions.setdefault(a, []).append(idx)
        interactions.setdefault(b, []).append(idx)

    test_idx = set()
    for author, idxs in interactions.items():
        if len(idxs) >= 2:
            chosen = int(rng.choice(idxs))
            test_idx.add(chosen)

    df_test = df_pairs_unique.loc[sorted(list(test_idx))].copy()
    df_train = df_pairs_unique.drop(index=list(test_idx)).copy()

    df_train = df_train.reset_index(drop=True)
    df_test = df_test.reset_index(drop=True)

    print(f"✔ Train unique: {len(df_train):,} | Test unique: {len(df_test):,}")
    return df_train, df_test

# -------------------------------
# 3) Construcción simétrica (explícita)
# -------------------------------
def build_symmetric(df_unique):
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
    df_sym["coauthor_1_idx"] = df_sym["coauthor_1"].map(author_to_idx)
    df_sym["coauthor_2_idx"] = df_sym["coauthor_2"].map(author_to_idx)

    n_missing = int(df_sym["coauthor_1_idx"].isna().sum()) + int(df_sym["coauthor_2_idx"].isna().sum())
    if n_missing > 0:
        print("❌ ERROR: existen IDs en df_sym que no están en author_to_idx:")
        print("  coauthor_1 missing:", df_sym["coauthor_1_idx"].isna().sum())
        print("  coauthor_2 missing:", df_sym["coauthor_2_idx"].isna().sum())
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
        # set scores to -inf for seen items
        scores[list(seen)] = -np.inf

    # también evitar recomendar al mismo autor
    scores[u] = -np.inf

    n_items = scores.shape[0]
    K_eff = min(K, n_items)

    # argpartition para eficiencia con arrays grandes
    idx_part = np.argpartition(-scores, K_eff - 1)[:K_eff]
    topk = idx_part[np.argsort(-scores[idx_part])]

    return topk

# -------------------------------
# 6) Evaluación LOO usando U
# -------------------------------
def recall_precision_at_k_sample_U(U, R_train, R_val, users, K=10):
    recall_list = []
    precision_list = []
    evaluados = 0

    # pre-extract pointers for speed
    val_indptr = R_val.indptr
    val_indices = R_val.indices
    train_indptr = R_train.indptr
    train_indices = R_train.indices

    for u in users:
        u = int(u)

        if R_train.getrow(u).nnz == 0:
            continue
        if R_val.getrow(u).nnz == 0:
            continue

        gt_items = val_indices[val_indptr[u]:val_indptr[u+1]]
        if len(gt_items) == 0:
            continue

        # obtener top-K pred usando U
        train_row = R_train.getrow(u)
        preds = top_k_from_U(U, u, train_row, K)

        if len(preds) == 0:
            continue

        hits = len(set(preds).intersection(set(gt_items)))
        recall_list.append(hits / len(gt_items))
        precision_list.append(hits / K)
        evaluados += 1

    if evaluados == 0:
        return 0.0, 0.0, 0

    return float(np.mean(recall_list)), float(np.mean(precision_list)), evaluados

# -------------------------------
# 7) Entrenamiento ALS y simetrización
# -------------------------------
def train_als_symmetric(R_train, factors=64, reg=0.01, iterations=15, num_threads=0, use_gpu=False):
    """
    Entrena ALS (implicit) y retorna embeddings simétricos U = (P + Q) / 2
    donde P = user_factors, Q = item_factors.
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

    P = model.user_factors  # shape (n_authors, factors)
    Q = model.item_factors  # shape (n_authors, factors)

    U = (P + Q) / 2.0
    return U.astype(np.float32), model

# -------------------------------
# 8) Pipeline principal
# -------------------------------
def run_full_recommendation_system(
    factors_list=[64, 128],
    reg_list=[0.01, 0.1],
    iterations=10,
    K=10,
    sample_users_eval=2000,
    random_state=42,
    save_dir=None
):
    """
    Ejecuta pipeline completo:
    - carga datos
    - LOO seguro
    - construye matrices simétricas
    - entrena ALS (simétrico) para cada combinación (grid search)
    - evalúa con recall/precision usando U
    - devuelve mejor configuración + embeddings/modelo
    """
    print("============================================================")
    print("🚀 SISTEMA DE RECOMENDACIÓN - ALS SIMÉTRICO (U·U^T)")
    print("============================================================")

    # 1) Carga
    df_pairs_unique, author_to_idx, author_list = get_author_map_and_ratings()

    # 2) LOO seguro
    df_train_unique, df_test_unique = leave_one_out_split(df_pairs_unique, seed=random_state)

    # 3) construir simétricos
    df_train_sym = build_symmetric(df_train_unique)
    df_test_sym = build_symmetric(df_test_unique)

    # 4) mapear y construir sparse
    R_train = map_indices_and_build(df_train_sym, author_to_idx)
    R_test = map_indices_and_build(df_test_sym, author_to_idx)

    R_train = R_train.tocsr().astype(np.float32)
    R_test = R_test.tocsr().astype(np.float32)

    print("DEBUG: R_train.shape, dtype:", R_train.shape, R_train.dtype)
    print("DEBUG: R_test.shape, dtype:", R_test.shape, R_test.dtype)

    # validar usuarios entre train/test
    train_users = set(np.where(R_train.getnnz(axis=1) > 0)[0])
    test_users = set(np.where(R_test.getnnz(axis=1) > 0)[0])
    missing = test_users - train_users
    print("🔎 Usuarios en test pero NO en train:", len(missing))
    if len(missing) > 0:
        print("⚠️ Algunos usuarios problemáticos (ejemplos):", list(missing)[:20])

    # conectividad
    n_users = R_train.shape[0]
    users_with_train = int((R_train.getnnz(axis=1) > 0).sum())
    users_with_test = int((R_test.getnnz(axis=1) > 0).sum())
    print(f"Usuarios totales (n): {n_users}")
    print(f"Usuarios con conexiones en train: {users_with_train}")
    print(f"Usuarios con conexiones en test: {users_with_test}")

    # 5) seleccionar muestra de usuarios válidos
    rng = np.random.default_rng(random_state)
    valid_train_users = np.where(R_train.getnnz(axis=1) > 0)[0]
    sample_users = rng.choice(valid_train_users, size=min(sample_users_eval, len(valid_train_users)), replace=False)

    # 6) grid search
    results = []
    best_score = -1.0
    best_model = None
    best_params = None

    for f in factors_list:
        for r in reg_list:
            print(f"\n🔧 Probando: factors={f}, regularization={r}, iterations={iterations}")
            t0 = time.time()

            U, model = train_als_symmetric(R_train, factors=f, reg=r, iterations=iterations)
            train_time = time.time() - t0

            rc, pr, n_eval = recall_precision_at_k_sample_U(U, R_train, R_test, sample_users, K=K)

            results.append({
                "factors": f,
                "regularization": r,
                "iterations": iterations,
                "Recall@K": rc,
                "Precision@K": pr,
                "Evaluados": n_eval,
                "Train_Sec": train_time
            })

            print(f"  → Recall@{K}: {rc:.6f} | Precision@{K}: {pr:.6f} | Evaluados: {n_eval} | Train: {train_time:.2f}s")

            if rc > best_score:
                best_score = rc
                best_model = (U, model)
                best_params = {"factors": f, "regularization": r, "iterations": iterations, "Recall@K": rc, "Precision@K": pr}

    # guardar resultados opcionalmente
    if save_dir is not None:
        os.makedirs(save_dir, exist_ok=True)
        # guardar embeddings U del mejor modelo
        if best_model is not None:
            U_best, model_best = best_model
            U_path = os.path.join(save_dir, "cf_U_als_symmetric.npy")
            model_path = os.path.join(save_dir, "cf_als_model.pkl")
            np.save(U_path, U_best.astype(np.float32))
            with open(model_path, "wb") as f:
                pickle.dump(model_best, f, protocol=pickle.HIGHEST_PROTOCOL)
            print(f"✅ Embeddings guardados en: {U_path}")
            print(f"✅ Modelo guardado en: {model_path}")

    df_results = pd.DataFrame(results).sort_values(["Precision@K", "Recall@K"], ascending=False).reset_index(drop=True)

    print("\n============================================================")
    print("🏆 MEJORES HIPERPARÁMETROS:")
    print(best_params)
    print("============================================================")

    return {"best_params": best_params, "results": df_results, "best_model": best_model, "author_list": author_list, "author_to_idx": author_to_idx}


