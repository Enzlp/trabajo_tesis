from pyalex import Concepts

# Crear cliente de Concepts
concepts_client = Concepts()

# ID del concepto padre (Computer Science)
cs_id = "https://openalex.org/C154945302"

# Filtrar conceptos que tengan a Computer Science como ancestro
derived_concepts = concepts_client.filter(**{"ancestors.id": cs_id}).get(per_page=200)

# Filtrar solo los que sean de nivel 1
level_1_concepts = [c for c in derived_concepts ]

# Mostrar resultados
print(f"Número de conceptos de nivel 1 bajo Computer Science: {len(level_1_concepts)}")
for c in level_1_concepts:
    print(f"- {c['display_name']} ({c['id']})")

# Lista de conceptos con ancestro Computer science y que son de IA

# - Artificial intelligence (https://openalex.org/C154945302) → el concepto principal de IA.
# - Machine learning (https://openalex.org/C119857082) → aprendizaje automático, subárea central de IA.
# - Computer vision (https://openalex.org/C31972630) → visión por computadora, subcampo de IA.
# - Data mining (https://openalex.org/C124101348) → extracción de conocimiento de datos, muy usado en IA/ML.
# - Data science (https://openalex.org/C2522767166) → ciencia de datos, relacionada con ML y análisis inteligente.
# - Natural language processing (https://openalex.org/C204321447) → procesamiento de lenguaje natural, subárea de IA.
# - Speech recognition (https://openalex.org/C28490314) → reconocimiento de voz, aplicación de IA/ML.


