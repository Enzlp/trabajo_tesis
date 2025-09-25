# ==============================================================================================
# Modelo basado en contenido para encontrar investigadores complementarios (interdisciplinarios)
# ==============================================================================================

from pyalex import Authors, Subfields, Works, Topics
import numpy as np
import pandas as pd

# Códigos de paises de LATAM
latam_countries = ['AR', 'BO', 'BR', 'CL', 'CO', 'CR', 'CU', 'DO', 'EC', 'SV', 'GT', 'HN', 'MX', 'NI', 'PA', 'PY', 'PE', 'PR', 'UY', 'VE']
latam_countries_str = "|".join(latam_countries)

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



# Matriz de coocurrencias: Calculamos la matriz de coocurrencias para usarla despues
n = len(topics_ia)
m = len(topics_total)
cooc_matrix = np.zeros((n, m))

for i, t_ia in enumerate(topics_ia):
    for j, t_total in enumerate(topics_total):
        count = Works().filter(
            topics={"id": [t_ia, t_total]}
        ).count()
        cooc_matrix[i, j] = count
        print(f"({i+1}/{n}, {j+1}/{m}) {t_ia}-{t_total}: {count}")

    # Guardar avance parcial en CSV después de cada fila
    df_partial = pd.DataFrame(cooc_matrix, index=topics_ia, columns=topics_total)
    df_partial.to_csv("cooc_matrix_partial.csv")
		
df_final = pd.DataFrame(cooc_matrix, index=topics_ia, columns=topics_total)
df_final.to_csv("cooc_matrix.csv")

# -------------- Caso Práctico ----------------

#works = Works().filter(
#    topics={"id": ["T10799", "T11106"]}
#).count()

