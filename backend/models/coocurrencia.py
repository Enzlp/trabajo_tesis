# ==============================================================================================
# Calculo de la matriz de coocurrencia entre topicos
# ==============================================================================================

from pyalex import Authors, Subfields, Works, Topics
import numpy as np
import pandas as pd

# Topicos de IA
topics_ia = [t['id'].split('/')[-1] for t in Subfields().filter(id=1702).get(per_page=200)[0]['topics']]

# Topicos restantes
topics_paginated = Topics().paginate(method="page", per_page=200)
topics_total = []
for page in topics_paginated:
	for item in page:
		id = item['id'].split('/')[-1]
		if id not in topics_ia:
			topics_total.append(id)

# Usaremos un valor menor de matriz para que no tome años el calculo
min_len = topics_total[:50]

# Matriz de coocurrencias: Calculamos la matriz de coocurrencias para usarla despues
print("Calculando matriz")
n = len(topics_ia)
#m = len(topics_total)
m = len(min_len)
cooc_matrix = np.zeros((n, m))

for i, t_ia in enumerate(topics_ia):
    for j, t_total in enumerate(min_len):
        count = Works().filter(
            topics={"id": [t_ia, t_total]}
        ).count()
        cooc_matrix[i, j] = count
        print(f"({i+1}/{n}, {j+1}/{m}) {t_ia}-{t_total}: {count}")

# Guardamos resultado para uso posterior
df = pd.DataFrame(
    cooc_matrix,
    index=topics_ia,
    columns=min_len
)

# Guardar en CSV
df.to_csv("cooc_matrix.csv", index=True)