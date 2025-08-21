from django.db import models

# -----------------------
# TABLAS DE ENTIDADES
# -----------------------
class Concept(models.Model):
    id = models.TextField(primary_key=True)
    wikidata = models.TextField(blank=True, null=True)
    display_name = models.TextField(blank=True, null=True)
    level = models.IntegerField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    works_count = models.IntegerField(blank=True, null=True)
    cited_by_count = models.IntegerField(blank=True, null=True)
    image_url = models.TextField(blank=True, null=True)
    image_thumbnail_url = models.TextField(blank=True, null=True)
    works_api_url = models.TextField(blank=True, null=True)
    updated_date = models.DateTimeField(blank=True, null=True)

    ancestors = models.ManyToManyField(
        "self",
        through="ConceptAncestor",
        symmetrical=False,
        related_name="descendants"
    )

    class Meta:
        db_table = "concepts"
        managed = True

class Work(models.Model):
    id = models.TextField(primary_key=True)
    doi = models.TextField(blank=True, null=True)
    title = models.TextField(blank=True, null=True)
    display_name = models.TextField(blank=True, null=True)
    publication_year = models.IntegerField(blank=True, null=True)
    publication_date = models.TextField(blank=True, null=True)
    type = models.TextField(blank=True, null=True)
    cited_by_count = models.IntegerField(blank=True, null=True)
    is_retracted = models.BooleanField(blank=True, null=True)
    is_paratext = models.BooleanField(blank=True, null=True)
    host_venue = models.TextField(blank=True, null=True)

    concepts = models.ManyToManyField(
        Concept,
        through="WorkConcept",
        related_name="works"
    )

    class Meta:
        db_table = "works"
        managed = True
        
class Author(models.Model):
    id = models.TextField(primary_key=True)
    orcid = models.TextField(blank=True, null=True)
    display_name = models.TextField(blank=True, null=True)
    display_name_alternatives = models.TextField(blank=True, null=True)
    works_count = models.IntegerField(blank=True, null=True)
    cited_by_count = models.IntegerField(blank=True, null=True)
    last_known_institution = models.TextField(blank=True, null=True)
    works_api_url = models.TextField(blank=True, null=True)
    updated_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = "authors"
        managed = True


class Institution(models.Model):
    id = models.TextField(primary_key=True)
    ror = models.TextField(blank=True, null=True)
    display_name = models.TextField(blank=True, null=True)
    country_code = models.TextField(blank=True, null=True)
    type = models.TextField(blank=True, null=True)
    homepage_url = models.TextField(blank=True, null=True)
    image_url = models.TextField(blank=True, null=True)
    image_thumbnail_url = models.TextField(blank=True, null=True)
    display_name_acronyms = models.TextField(blank=True, null=True)
    display_name_alternatives = models.TextField(blank=True, null=True)
    works_count = models.IntegerField(blank=True, null=True)
    cited_by_count = models.IntegerField(blank=True, null=True)
    works_api_url = models.TextField(blank=True, null=True)
    updated_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = "institutions"
        managed = True

class Venue(models.Model):
    id = models.TextField(primary_key=True)
    issn_l = models.TextField(blank=True, null=True)
    issn = models.TextField(blank=True, null=True)
    display_name = models.TextField(blank=True, null=True)
    publisher = models.TextField(blank=True, null=True)
    works_count = models.IntegerField(blank=True, null=True)
    cited_by_count = models.IntegerField(blank=True, null=True)
    is_oa = models.BooleanField(blank=True, null=True)
    is_in_doaj = models.BooleanField(blank=True, null=True)
    homepage_url = models.TextField(blank=True, null=True)
    works_api_url = models.TextField(blank=True, null=True)
    updated_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = "venues"
        managed = True
        

# -----------------------
# TABLAS DE RELACIONES
# -----------------------

class ConceptAncestor(models.Model):
    concept_id = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name="concept_ancestor_links")
    ancestor_id = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name="ancestor_concept_links")

    class Meta:
        db_table = "concepts_ancestors"
        managed = True
        unique_together = (("concept", "ancestor"),)
        
class ConceptRelatedConcept(models.Model):
    concept_id = models.ForeignKey(
        Concept,
        on_delete=models.CASCADE,
        related_name="related_concept_links"
    )
    related_concept_id = models.ForeignKey(
        Concept,
        on_delete=models.CASCADE,
        related_name="related_to_links"
    )
    score = models.FloatField(blank=True, null=True)

    class Meta:
        db_table = "concepts_related_concepts"
        managed = True
        unique_together = (("concept", "related_concept"),)

class WorkConcept(models.Model):
    work_id = models.ForeignKey(
        Work,
        on_delete=models.CASCADE,
        related_name= "related_work_links"
	)
    concept_id = models.ForeignKey(
        Concept,
        on_delete=models.CASCADE,
        related_name="related_concept_links"
	)
    score=models.FloatField(blank=True, null=True)

    class Meta:
        db_table = "works_concepts"
        managed = True
        
class WorksAuthorship(models.Model):
    work_id = models.ForeignKey(
        Work,
        on_delete=models.CASCADE,
        related_name="related_work"
    )
    author_position = models.TextField(blank=True, null=True)
    author_id = models.ForeignKey(
        Author,
        on_delete=models.CASCADE,
        related_name="related_author"
    )
    institution_id = models.ForeignKey(
        Institution,
        on_delete=models.CASCADE,
        related_name="related_institution"
    )

    class Meta:
        db_table = "works_authorships"
        managed = True

class WorkRelatedWork(models.Model):
    work_id=models.ForeignKey(
        Work,
        on_delete=models.CASCADE,
        related_name="related_work"
	)
    related_work_id=models.ForeignKey(
        Work,
        on_delete=models.CASCADE,
        related_name="related_to_work"
	)
    class Meta:
        db_table = "works_related_works"
        managed = True    
        
class WorkReferencedWork(models.Model):
    work_id = models.ForeignKey(
        Work,
        on_delete=models.CASCADE,
        related_name="referenced_work"
	)
    referenced_work_id=models.ForeignKey(
        Work,
        on_delete=models.CASCADE,
        related_name="referenced_to_work"
	)
    class Meta:
        db_table = "works_referenced_works"
        managed = True  
        
class InstitutionAssociatedInstitution(models.Model):
    institution_id = models.ForeignKey(
        Institution,
        on_delete=models.CASCADE,
        related_name="associated_institution"
	)
    associated_institution_id = models.ForeignKey(
        Institution,
        on_delete=models.CASCADE,
        relate_name="associated_to_institution"
	)
    relationship = models.TextField()
    class Meta:
        db_table = "institutions_associated_institutions"
        managed = True

class WorkAlternateHostVenue(models.Model):
    work_id = models.ForeignKey(Work, on_delete=models.CASCADE, related_name="alternate_venues")
    venue_id = models.ForeignKey(Venue, on_delete=models.CASCADE, related_name="alternate_works")

    class Meta:
        db_table = "works_alternate_host_venues"
        managed = True
        unique_together = (("work", "venue"),)


class WorkBiblio(models.Model):
    work_id = models.OneToOneField(Work, on_delete=models.CASCADE, primary_key=True)
    volume = models.TextField(blank=True, null=True)
    issue = models.TextField(blank=True, null=True)
    first_page = models.TextField(blank=True, null=True)
    last_page = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "works_biblio"
        managed = True


class WorkMesh(models.Model):
    work_id = models.ForeignKey(Work, on_delete=models.CASCADE, related_name="mesh_terms")
    descriptor_ui = models.TextField(blank=True, null=True)
    descriptor_name = models.TextField(blank=True, null=True)
    qualifier_ui = models.TextField(blank=True, null=True)
    qualifier_name = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "works_mesh"
        managed = True


class WorkOpenAccess(models.Model):
    work_id = models.OneToOneField(Work, on_delete=models.CASCADE, primary_key=True)
    is_oa = models.BooleanField(blank=True, null=True)
    oa_status = models.TextField(blank=True, null=True)
    oa_url = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "works_open_access"
        managed = True

class ConceptID(models.Model):
    concept_id = models.OneToOneField(Concept, on_delete=models.CASCADE, primary_key=True)
    openalex = models.TextField(blank=True, null=True)
    wikidata = models.TextField(blank=True, null=True)
    wikipedia = models.TextField(blank=True, null=True)
    umls_aui = models.TextField(blank=True, null=True)
    umls_cui = models.TextField(blank=True, null=True)
    mag = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = "concepts_ids"
        managed = True


class WorkID(models.Model):
    work_id = models.OneToOneField(Work, on_delete=models.CASCADE, primary_key=True)
    openalex = models.TextField(blank=True, null=True)
    doi = models.TextField(blank=True, null=True)
    mag = models.IntegerField(blank=True, null=True)
    pmid = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "works_ids"
        managed = True


class AuthorID(models.Model):
    author_id = models.OneToOneField(Author, on_delete=models.CASCADE, primary_key=True)
    openalex = models.TextField(blank=True, null=True)
    orcid = models.TextField(blank=True, null=True)
    scopus = models.TextField(blank=True, null=True)
    twitter = models.TextField(blank=True, null=True)
    wikipedia = models.TextField(blank=True, null=True)
    mag = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = "authors_ids"
        managed = True


class VenueID(models.Model):
    venue_id = models.OneToOneField(Venue, on_delete=models.CASCADE, primary_key=True)
    openalex = models.TextField(blank=True, null=True)
    issn_l = models.TextField(blank=True, null=True)
    issn = models.TextField(blank=True, null=True)
    mag = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = "venues_ids"
        managed = True


class InstitutionID(models.Model):
    institution_id = models.OneToOneField(Institution, on_delete=models.CASCADE, primary_key=True)
    openalex = models.TextField(blank=True, null=True)
    ror = models.TextField(blank=True, null=True)
    grid = models.TextField(blank=True, null=True)
    wikipedia = models.TextField(blank=True, null=True)
    wikidata = models.TextField(blank=True, null=True)
    mag = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = "institutions_ids"
        managed = True

class ConceptCountByYear(models.Model):
    concept_id = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name="counts_by_year")
    year = models.IntegerField()
    works_count = models.IntegerField(blank=True, null=True)
    cited_by_count = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = "concepts_counts_by_year"
        managed = True
        unique_together = (("concept", "year"),)


class AuthorCountByYear(models.Model):
    author_id = models.ForeignKey(Author, on_delete=models.CASCADE, related_name="counts_by_year")
    year = models.IntegerField()
    works_count = models.IntegerField(blank=True, null=True)
    cited_by_count = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = "authors_counts_by_year"
        managed = True
        unique_together = (("author", "year"),)


class VenueCountByYear(models.Model):
    venue_id = models.ForeignKey(Venue, on_delete=models.CASCADE, related_name="counts_by_year")
    year = models.IntegerField()
    works_count = models.IntegerField(blank=True, null=True)
    cited_by_count = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = "venues_counts_by_year"
        managed = True
        unique_together = (("venue", "year"),)


class InstitutionCountByYear(models.Model):
    institution_id = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name="counts_by_year")
    year = models.IntegerField()
    works_count = models.IntegerField(blank=True, null=True)
    cited_by_count = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = "institutions_counts_by_year"
        managed = True
        unique_together = (("institution", "year"),)

class InstitutionGeo(models.Model):
    institution_id = models.OneToOneField(Institution, on_delete=models.CASCADE, primary_key=True)
    city = models.TextField(blank=True, null=True)
    geonames_city_id = models.TextField(blank=True, null=True)
    region = models.TextField(blank=True, null=True)
    country_code = models.TextField(blank=True, null=True)
    country = models.TextField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)

    class Meta:
        db_table = "institutions_geo"
        managed = True

