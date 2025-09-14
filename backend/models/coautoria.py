# =======================================================================
# Modelo de Collaborative Filtering para redes de coautoría
# =======================================================================

# Si un investigador A colabora con los mismos investigadores que investigador B, entonces es muy probable que el resto de investigadores
# con los que colabore B tambien le gusten a A

# El rating será el numero de papers entre invesitgador A y C. Se normalizan los valores para que obtengan el mismo peso los autores mas y menos productivos,
# puede ser normalizado binario (0 o 1 si hay al menos una colaboracion), o por frecuencia total. El enfoque binario evita que haya opacacion por investigadores con mayor cantidad de papers lo que
# ayuda a crear nuevos contactos, el enfoque de frecuencia ayuda a que se evidencie la fuerza de relacion entre autores, entre mas colaboraciones entre dos autores 
# sobre el total, mas fuerte es la relacion entre esos dos autores. Finalmente, lo que conviene mas es la normalizacion por frecuencia



