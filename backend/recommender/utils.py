import numpy as np

def cosine_similarity(vec_a,vec_b):
  if vec_a.shape != vec_b.shape:
      raise ValueError("Los vectores deben tener la misma dimensión")

  dot_product = np.dot(vec_a, vec_b)
  norm_a = np.linalg.norm(vec_a)
  norm_b = np.linalg.norm(vec_b) 

  if norm_a == 0.0 or norm_b == 0.0:
    return 0.0

  return float(dot_product / (norm_a * norm_b))

