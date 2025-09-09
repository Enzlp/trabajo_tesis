# Descarga de una muestra de OpenAlex para desarrollo, aprox 40000 autores latinoamericanos con sus entidades relacionadas
# usando libreria PyAlex (el sample usa sudamerica y no latinoamerica)

from pyalex import Authors, Works, Institutions, Sources, Topics, Publishers, Funders, Subfields

# funcion para subir autor a base de datos
def upload_data(id):
    author = Authors().filter(id=id).get()
    pass

# Codigos paises latinoamericanos
latam_countries = ['AR', 'BO', 'BR', 'CL', 'CO', 'CR', 'CU', 'DO', 'EC', 'SV', 'GT', 'HN', 'MX',
            'NI', 'PA', 'PY', 'PE', 'PR', 'UY', 'VE']

# Topics en el subfield IA (1702)
topic_ids = [t['id'].split('/')[-1] for t in Subfields().filter(id=1702).get(per_page=200)[0]['topics']]

# Usamos un set para almacenar IDs de autores únicos
author_ids_set = set()

# Obtenemos 40000 autores en IA en latinoamerica
for country in latam_countries:
    for t_id in topic_ids:
        authors = Authors().filter(
            **{
                "last_known_institutions.country_code": country,
                "topics.id": t_id
            }
        ).get(per_page=200)
        
        for a in authors:
            author_ids_set.add(a['id'].split('/')[-1])  # agrega sin preocuparse de duplicados
        
        if len(author_ids_set) >= 1000:
            break
    if len(author_ids_set) >= 40000:
        break

# Convertimos a lista y recortamos a los primeros 1000
author_ids = list(author_ids_set)

# Total de autores en IA y latinoamerica: aprox 213192
