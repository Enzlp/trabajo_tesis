# ==============================================================================================
# Calculo de la matriz de coocurrencia entre topicos de ia
# ==============================================================================================

from pyalex import Subfields

#  Topicos de IA
topics_ia = [t['id'].split('/')[-1] for t in Subfields().filter(id=1702).get(per_page=200)[0]['topics']]

