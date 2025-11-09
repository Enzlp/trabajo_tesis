import os
from api.models import MvIaConceptView
import pickle

"""
Crea un archivo con el mapeo de conceptos a indices
"""
def map_concepts(files_dir):
	concepts = MvIaConceptView.objects.values_list("id", flat=True).order_by("id")
	concept_mapping = {concept_id: idx for idx, concept_id in enumerate(concepts)}
	file_path = os.path.join(files_dir, 'concept_mapping.pkl')
	with open(file_path, "wb") as f:
		pickle.dump(concept_mapping, f, protocol=pickle.HIGHEST_PROTOCOL)