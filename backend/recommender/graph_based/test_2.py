import os
import pickle
import numpy as np
import torch

def load_embeddings(files_path):
    """Carga embeddings y mapeo desde disco"""
    embeddings_path = os.path.join(files_path, "embeddings.npy")
    mapping_path = os.path.join(files_path, "author_to_idx.pkl")
    
    if not os.path.exists(embeddings_path) or not os.path.exists(mapping_path):
        raise FileNotFoundError("No se encontraron embeddings o mapeo. Ejecuta primero el script de entrenamiento.")
    
    embeddings = torch.from_numpy(np.load(embeddings_path))
    with open(mapping_path, "rb") as f:
        author_to_idx = pickle.load(f)
    
    idx_to_author = {idx: author_id for author_id, idx in author_to_idx.items()}
    
    return embeddings, author_to_idx, idx_to_author

def find_similar_authors(author_idx, embeddings, top_k=10, batch_size=1000):
    """Encuentra autores similares sin matriz NxN completa"""
    embeddings_norm = embeddings / (embeddings.norm(dim=1, keepdim=True) + 1e-8)
    author_emb = embeddings_norm[author_idx].unsqueeze(0)
    num_nodes = embeddings_norm.size(0)

    all_scores = []
    all_indices = []

    for start in range(0, num_nodes, batch_size):
        end = min(start + batch_size, num_nodes)
        batch_emb = embeddings_norm[start:end]
        batch_scores = (author_emb @ batch_emb.T).squeeze(0)
        all_scores.append(batch_scores)
        all_indices.append(torch.arange(start, end))

    scores = torch.cat(all_scores)
    indices = torch.cat(all_indices)

    top_scores, top_positions = torch.topk(scores, min(top_k, len(scores)))
    top_indices = indices[top_positions]

    return top_indices.tolist(), top_scores.tolist()

def recommend_for_author(author_id, files_path, top_k=30):
    embeddings, author_to_idx, idx_to_author = load_embeddings(files_path)

    if author_id not in author_to_idx:
        raise ValueError(f"Autor ID {author_id} no encontrado en embeddings.")

    author_idx = author_to_idx[author_id]
    similar_indices, similar_scores = find_similar_authors(author_idx, embeddings, top_k=top_k)

    recommendations = []
    for rank, (idx, score) in enumerate(zip(similar_indices, similar_scores), 1):
        recommendations.append({
            "rank": rank,
            "author_id": idx_to_author[idx],
            "score": float(score)
        })

    return recommendations

# ===================== EJEMPLO DE USO =====================

if __name__ == "__main__":
    # Carpeta donde se guardaron los embeddings
    files_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Cambia por el autor que quieras
    author_id = "https://openalex.org/A5038897083"

    top_k = 30
    recs = recommend_for_author(author_id, files_path, top_k=top_k)

    print(f"\nRecomendaciones para autor {author_id}:\n" + "="*50)
    for r in recs:
        print(f"{r['rank']:2d}. {r['author_id']} | score = {r['score']:.4f}")
