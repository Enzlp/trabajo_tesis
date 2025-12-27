import os
import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix, save_npz
from api.models import MvIaCoauthorshipLatam

def prepare_turbocf_loo(files_dir):
    """
    Genera latam_train.npz, latam_val.npz y latam_test.npz usando Leave-One-Out.
    """
    print("📌 Preparando split Leave-One-Out (LOO) para TurboCF...")

    # 1) Cargar datos
    queryset = MvIaCoauthorshipLatam.objects.all().values(
        "coauthor_1", "coauthor_2", "shared_works"
    )
    
    raw_data = []
    all_authors = set()
    for row in queryset:
        a, b = str(row["coauthor_1"]), str(row["coauthor_2"])
        if a == b: continue
        all_authors.add(a)
        all_authors.add(b)
        raw_data.append({"a": a, "b": b, "w": float(row["shared_works"] or 0.0)})

    author_list = sorted(all_authors)
    author_to_idx = {aid: i for i, aid in enumerate(author_list)}
    n = len(author_list)

    # 2) Organizar por pares únicos para evitar fugas
    df = pd.DataFrame(raw_data)
    df["p1"] = np.where(df["a"] < df["b"], df["a"], df["b"])
    df["p2"] = np.where(df["a"] < df["b"], df["b"], df["a"])
    df = df.drop_duplicates(subset=["p1", "p2"]).sample(frac=1, random_state=2022)

    # 3) Aplicar LOO por autor
    # Agrupamos por p1 para asegurar que cada autor pierda una interacción
    # (En redes simétricas, esto es suficiente para el split LOO)
    df_test = df.groupby('p1').head(1)
    df_remaining = df.drop(df_test.index)
    
    df_val = df_remaining.groupby('p1').head(1)
    df_train = df_remaining.drop(df_val.index)

    def build_csr(dataframe, n_size):
        rows, cols, data = [], [], []
        for _, row in dataframe.iterrows():
            i, j = author_to_idx[row["p1"]], author_to_idx[row["p2"]]
            w = row["w"]
            rows.extend([i, j])
            cols.extend([j, i])
            data.extend([w, w])
        return csr_matrix((data, (rows, cols)), shape=(n_size, n_size), dtype=np.float32)

    # 4) Construir Matrices
    R_train = build_csr(df_train, n)
    R_val = build_csr(df_val, n)
    R_test = build_csr(df_test, n)

    if files_dir:
        os.makedirs(files_dir, exist_ok=True)
        save_npz(os.path.join(files_dir, "latam_train.npz"), R_train)
        save_npz(os.path.join(files_dir, "latam_val.npz"), R_val)
        save_npz(os.path.join(files_dir, "latam_test.npz"), R_test)
        np.save(os.path.join(files_dir, "cf_author_to_idx.npy"), author_to_idx)

    print(f"✅ Matrices LOO listas.")
    print(f"Train: {R_train.nnz:,} | Val: {R_val.nnz:,} | Test: {R_test.nnz:,}")