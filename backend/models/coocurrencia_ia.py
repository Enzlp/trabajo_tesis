# ==============================================================================================
# Calculo de la matriz de coocurrencia entre topicos de ia
# ==============================================================================================

from pyalex import Subfields, Works
import pandas as pd
import numpy as np

#  Topicos de IA
topics_ia = [t['id'].split('/')[-1] for t in Subfields().filter(id=1702).get(per_page=200)[0]['topics']]

m = len(topics_ia)
cooc_matrix = np.zeros((m, m))

# matriz de coocurrencia optimizada
for i, t_ia_1 in enumerate(topics_ia):
    for j in range(i, m):  # solo parte superior (incluye diagonal)
        if i == j:
            count = 0
        else:
            count = Works().filter(
                topics={"id": [t_ia_1, topics_ia[j]]}
            ).count()
        cooc_matrix[i, j] = count
        cooc_matrix[j, i] = count   # espejo
        print(f"({i+1}/{m}, {j+1}/{m}) {t_ia_1}-{topics_ia[j]}: {count}")



df = pd.DataFrame(
    cooc_matrix,
    index=topics_ia,
    columns=topics_ia
)

# Guardar en CSV
df.to_csv("cooc_matrix_ia.csv", index=True)