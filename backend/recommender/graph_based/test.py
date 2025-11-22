import sys 
import os
import pickle
import numpy as np

# Establece raiz del proyecto como path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")

import django
django.setup()

import torch
from torch import nn
import random
from api.models import LatamIaCoauthorshipView

def obtain_authors_lightgcn():
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

    return author_to_idx

def generate_edgelist_lightgcn(files_dir, author_to_idx):
    output_path = os.path.join(files_dir, "coauthor_edges.edgelist")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
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
                if a not in author_to_idx or b not in author_to_idx:
                    continue

                u = author_to_idx[a]
                v = author_to_idx[b]
                
                if u == v:
                    continue
                if w is None or w <= 0:
                    continue

                # grafo no dirigido → agregamos ambas direcciones
                f.write(f"{u} {v}\n")
                f.write(f"{v} {u}\n")

            offset += batch_size

    return output_path

def load_edgelist_streaming(path):
    """Carga edges directamente a tensor sin lista intermedia"""
    edges_u = []
    edges_v = []
    
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) != 2:
                continue
            u, v = map(int, parts)
            edges_u.append(u)
            edges_v.append(v)
    
    # Convertir directamente a tensor
    edge_index = torch.stack([
        torch.tensor(edges_u, dtype=torch.long),
        torch.tensor(edges_v, dtype=torch.long)
    ], dim=0)
    
    return edge_index

def split_edge_index(edge_index, test_ratio=0.2):
    """Split edge_index directamente sin lista intermedia"""
    num_edges = edge_index.size(1)
    perm = torch.randperm(num_edges)
    
    n_test = int(num_edges * test_ratio)
    test_idx = perm[:n_test]
    train_idx = perm[n_test:]
    
    train_edge_index = edge_index[:, train_idx]
    test_edge_index = edge_index[:, test_idx]
    
    return train_edge_index, test_edge_index

class LightGCN(nn.Module):
    def __init__(self, num_nodes, embedding_dim=64, num_layers=3):
        super().__init__()
        self.embedding = nn.Embedding(num_nodes, embedding_dim)
        nn.init.xavier_uniform_(self.embedding.weight)
        self.num_layers = num_layers

    def forward(self, edge_index):
        x = self.embedding.weight
        row, col = edge_index
        num_nodes = x.size(0)

        # grado
        deg = torch.bincount(row, minlength=num_nodes).float()
        deg_inv_sqrt = deg.pow(-0.5)
        deg_inv_sqrt[deg_inv_sqrt == float("inf")] = 0

        all_embeddings = [x]

        for _ in range(self.num_layers):
            # LightGCN propagation: x_j / sqrt(d_i * d_j)
            m = deg_inv_sqrt[row].unsqueeze(1) * x[col]
            x = torch.zeros_like(x)
            x.index_add_(0, row, m)
            x = x * deg_inv_sqrt.unsqueeze(1)
            all_embeddings.append(x)

        return torch.mean(torch.stack(all_embeddings, dim=0), dim=0)

def bpr_loss(edge_index, embeddings, num_nodes, num_neg_samples=1):
    """BPR loss corregido con muestreo de negativos"""
    num_edges = edge_index.size(1)
    
    # Samplear subset de edges para cada batch
    sample_size = min(10000, num_edges)
    sample_idx = torch.randint(0, num_edges, (sample_size,))
    
    users = edge_index[0, sample_idx]
    pos_items = edge_index[1, sample_idx]
    
    # Muestreo de negativos (asegurar que no sean positivos)
    neg_items = torch.randint(0, num_nodes, (sample_size,))
    
    user_emb = embeddings[users]
    pos_emb = embeddings[pos_items]
    neg_emb = embeddings[neg_items]
    
    pos_score = (user_emb * pos_emb).sum(dim=1)
    neg_score = (user_emb * neg_emb).sum(dim=1)
    
    loss = -torch.log(torch.sigmoid(pos_score - neg_score) + 1e-8).mean()
    
    # Regularización L2
    reg_loss = (user_emb.norm(2).pow(2) + pos_emb.norm(2).pow(2) + neg_emb.norm(2).pow(2)) / sample_size
    
    return loss + 1e-5 * reg_loss

def save_embeddings(embeddings, author_to_idx, files_path):
    """Guarda embeddings y mapeo en disco"""
    embeddings_path = os.path.join(files_path, "embeddings.npy")
    mapping_path = os.path.join(files_path, "author_to_idx.pkl")
    
    # Guardar embeddings como numpy array
    np.save(embeddings_path, embeddings.detach().cpu().numpy())
    
    # Guardar mapeo
    with open(mapping_path, "wb") as f:
        pickle.dump(author_to_idx, f)
    
    print(f"✅ Embeddings guardados en: {embeddings_path}")
    print(f"✅ Mapeo guardado en: {mapping_path}")

def load_embeddings(files_path):
    """Carga embeddings y mapeo desde disco"""
    embeddings_path = os.path.join(files_path, "embeddings.npy")
    mapping_path = os.path.join(files_path, "author_to_idx.pkl")
    
    if not os.path.exists(embeddings_path) or not os.path.exists(mapping_path):
        return None, None
    
    embeddings = torch.from_numpy(np.load(embeddings_path))
    with open(mapping_path, "rb") as f:
        author_to_idx = pickle.load(f)
    
    print(f"✅ Embeddings cargados desde: {embeddings_path}")
    return embeddings, author_to_idx

def find_similar_authors(author_idx, embeddings, top_k=10, batch_size=1000):
    """
    Encuentra autores similares sin crear matriz NxN completa.
    Calcula similitud en batches para ahorrar memoria.
    """
    # Normalizar embeddings para usar cosine similarity
    embeddings_norm = embeddings / (embeddings.norm(dim=1, keepdim=True) + 1e-8)
    author_emb = embeddings_norm[author_idx].unsqueeze(0)
    
    num_nodes = embeddings_norm.size(0)
    
    all_scores = []
    all_indices = []
    
    # Procesar en batches
    for start in range(0, num_nodes, batch_size):
        end = min(start + batch_size, num_nodes)
        batch_emb = embeddings_norm[start:end]
        
        # Calcular similitud coseno
        batch_scores = (author_emb @ batch_emb.T).squeeze(0)
        
        all_scores.append(batch_scores)
        all_indices.append(torch.arange(start, end))
    
    # Concatenar resultados
    scores = torch.cat(all_scores)
    indices = torch.cat(all_indices)
    
    # Obtener top-k
    top_scores, top_positions = torch.topk(scores, min(top_k, len(scores)))
    top_indices = indices[top_positions]
    
    return top_indices.tolist(), top_scores.tolist()

# ===================== MAIN =====================

print("🚀 Iniciando LightGCN para Recomendación de Coautores")
print("=" * 70)

files_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Intentar cargar embeddings existentes
print("\n📂 Verificando embeddings existentes...")
embeddings, author_to_idx = load_embeddings(files_path)

if embeddings is None:
    print("\n🔨 ENTRENANDO MODELO DESDE CERO")
    print("=" * 70)
    
    # Cargar datos
    print("\n1️⃣  Obteniendo autores...")
    author_to_idx = obtain_authors_lightgcn()
    num_nodes = len(author_to_idx)
    print(f"   ✓ Total de autores: {num_nodes:,}")
    
    print("\n2️⃣  Generando edge list...")
    edge_path = generate_edgelist_lightgcn(files_path, author_to_idx)
    print(f"   ✓ Archivo generado: {edge_path}")
    
    print("\n3️⃣  Cargando edges...")
    edge_index = load_edgelist_streaming(edge_path)
    num_edges = edge_index.size(1)
    print(f"   ✓ Total de edges: {num_edges:,}")
    
    print("\n4️⃣  Dividiendo dataset (80% train, 20% test)...")
    train_edge_index, test_edge_index = split_edge_index(edge_index, test_ratio=0.2)
    print(f"   ✓ Train edges: {train_edge_index.size(1):,}")
    print(f"   ✓ Test edges: {test_edge_index.size(1):,}")
    
    # Liberar memoria
    del edge_index
    
    print("\n5️⃣  Inicializando modelo...")
    model = LightGCN(num_nodes=num_nodes, embedding_dim=64, num_layers=3)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.005, weight_decay=1e-5)
    print(f"   ✓ Modelo creado con {num_nodes:,} nodos")
    
    print("\n6️⃣  Entrenando modelo...")
    print("   Epochs: 100 | Batch size: 10K edges")
    print("-" * 70)
    
    for epoch in range(100):
        model.train()
        optimizer.zero_grad()
        
        # Forward pass
        embeddings = model(train_edge_index)
        
        # Calcular loss
        loss = bpr_loss(train_edge_index, embeddings, num_nodes)
        
        # Backward pass
        loss.backward()
        optimizer.step()
        
        if epoch % 10 == 0:
            print(f"   Epoch {epoch:3d} | Loss: {loss.item():.6f}")
    
    print("\n   ✓ Entrenamiento completado!")
    
    # Obtener embeddings finales
    print("\n7️⃣  Generando embeddings finales...")
    model.eval()
    with torch.no_grad():
        embeddings = model(train_edge_index)
    
    # Guardar embeddings
    print("\n8️⃣  Guardando embeddings...")
    save_embeddings(embeddings, author_to_idx, files_path)
    
    print("\n" + "=" * 70)
    print("✅ MODELO ENTRENADO Y GUARDADO EXITOSAMENTE")
else:
    print("✅ Embeddings cargados desde disco")
    num_nodes = len(author_to_idx)
    print(f"   Total de autores: {num_nodes:,}")

# ===================== EJEMPLO DE USO =====================

print("\n" + "=" * 70)
print("🔍 EJEMPLO: BÚSQUEDA DE AUTORES SIMILARES")
print("=" * 70)

# Crear mapeo inverso
idx_to_author = {idx: author_id for author_id, idx in author_to_idx.items()}

# Ejemplo con primer autor
example_author_id = list(author_to_idx.keys())[0]
author_idx = author_to_idx[example_author_id]

print(f"\n📊 Buscando similares para autor ID {example_author_id} (índice {author_idx}):")
print("-" * 70)

similar_indices, similar_scores = find_similar_authors(author_idx, embeddings, top_k=10)

for rank, (idx, score) in enumerate(zip(similar_indices, similar_scores), 1):
    original_id = idx_to_author[idx]
    marker = "⭐" if idx == author_idx else "  "
    print(f"{marker} {rank:2d}. Autor ID {original_id} (índice {idx}): score = {score:.4f}")

print("\n" + "=" * 70)
print("✅ Script completado exitosamente!")
print(f"💾 Memoria usada por embeddings: ~{(num_nodes * 64 * 4) / (1024**2):.1f} MB")
print("=" * 70)