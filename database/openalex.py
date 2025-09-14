# Descarga una muestra de OpenAlex para desarrollo, aprox 40000 autores latinoamericanos con sus entidades relacionadas
# usando libreria PyAlex (el sample usa sudamerica y no latinoamerica)

from pyalex import Authors, Works, Institutions, Sources, Topics, Publishers, Funders, Subfields
import json


# Codigos paises latinoamericanos
latam_countries = ['AR', 'BO', 'BR', 'CL', 'CO', 'CR', 'CU', 'DO', 'EC', 'SV', 'GT', 'HN', 'MX',
            'NI', 'PA', 'PY', 'PE', 'PR', 'UY', 'VE']

# Topics en el subfield IA (1702)
topic_ids = [t['id'].split('/')[-1] for t in Subfields().filter(id=1702).get(per_page=200)[0]['topics']]

# Obtenemos el numero de autores vinculados a IA y en LATAM: aprox 139394
latam_countries_str = "|".join(latam_countries)
topics_str = "|".join(topic_ids)

authors_count = Authors().filter(            **{
                "last_known_institutions.country_code": latam_countries_str,
                "topics.id": topics_str
            }).count()

# Usamos un set para almacenar IDs de autores únicos
author_ids_set = set()

# Obtenemos 10000 autores en IA en latinoamerica
count = 0

authors = Authors().filter(
        **{
            "last_known_institutions.country_code": latam_countries_str,
            "topics.id": topics_str
        }
    ).paginate(method="page", per_page=200)

for page in authors:

    if not page or count >= 10000:
        break

    for a in page:
        author_ids_set.add(a['id'].split('/')[-1])

    count += len(page)


# Convertimos a lista 
author_ids = list(author_ids_set)
print(author_ids[0])

