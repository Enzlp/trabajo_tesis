
# ==============================================================================
# Crea un archivo con mapeo de conceptos a indices
# ==============================================================================

import sys
import os

# Agregar la raíz del proyecto al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")

import django
django.setup()


from api.models import MvIaConceptView
import pickle

# Obtener los conceptos ordenados
concepts = MvIaConceptView.objects.values_list("id", flat=True).order_by("id")

# Crear el mapeo id → índice
concept_mapping = {concept_id: idx for idx, concept_id in enumerate(concepts)}

# Guardar como Pickle
with open("recommender/files/concept_mapping.pkl", "wb") as f:
    pickle.dump(concept_mapping, f, protocol=pickle.HIGHEST_PROTOCOL)

print(f"Generados {len(concept_mapping)} conceptos en ambos formatos.")
