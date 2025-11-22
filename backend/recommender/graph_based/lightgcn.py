import sys 
import os

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

def load_edgelist(path):
    edges = []

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) != 2:
                continue
            u, v = map(int, parts)
            edges.append((u, v))

    return edges

def split_edges(edges, test_ratio=0.2):
    random.shuffle(edges)
    n_test = int(len(edges) * test_ratio)
    test_edges = edges[:n_test]
    train_edges = edges[n_test:]
    return train_edges, test_edges

def build_edge_index(edges):
    src = torch.tensor([u for u, _ in edges], dtype=torch.long)
    dst = torch.tensor([v for _, v in edges], dtype=torch.long)
    return torch.stack([src, dst], dim=0)

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

def bpr_loss(edge_index, embeddings, num_nodes):
    users = edge_index[0]
    pos_items = edge_index[1]

    # muestreamos negativos
    neg_items = torch.randint(0, num_nodes, (len(users),), device=embeddings.device)

    user_emb = embeddings[users]
    pos_emb = embeddings[pos_items]
    neg_emb = embeddings[neg_items]

    pos_score = (user_emb * pos_emb).sum(dim=1)
    neg_score = (user_emb * neg_emb).sum(dim=1)

    loss = -torch.log(torch.sigmoid(pos_score - neg_score) + 1e-8).mean()
    return loss

# cargar datos
author_to_idx = obtain_authors_lightgcn()
num_nodes = len(author_to_idx)
print("Num nodes: ", num_nodes)

files_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
edge_path = generate_edgelist_lightgcn(files_path, author_to_idx)

edges = load_edgelist(edge_path)
train_edges, test_edges = split_edges(edges)

edge_index = build_edge_index(train_edges)

print("Entrenar modelo")
model = LightGCN(num_nodes=num_nodes, embedding_dim=64, num_layers=3)
optimizer = torch.optim.Adam(model.parameters(), lr=0.01)

# entrenamiento
for epoch in range(100):
    optimizer.zero_grad()
    embeddings = model(edge_index)
    loss = bpr_loss(edge_index, embeddings, num_nodes)
    loss.backward()
    optimizer.step()

    if epoch % 10 == 0:
        print(f"Epoch {epoch}: Loss {loss.item():.4f}")

# similitud por dot-product
scores = embeddings @ embeddings.T  # (num_nodes, num_nodes)

# top-10 vecinos de autor 0
top10 = torch.topk(scores[0], 10).indices.tolist()

