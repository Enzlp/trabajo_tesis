-- Seguimos DB recomendado por Openalex

-- Creamos el esquema
CREATE SCHEMA IF NOT EXISTS openalex;

-- ========================================
-- TABLAS PRINCIPALES
-- ========================================

-- Crear tabla concepts (tabla principal de conceptos)
CREATE TABLE concepts (
    id TEXT PRIMARY KEY,
    wikidata TEXT,
    display_name TEXT,
    level INTEGER,
    description TEXT,
    works_count INTEGER,
    cited_by_count INTEGER,
    image_url TEXT,
    image_thumbnail_url TEXT,
    works_api_url TEXT,
    updated_date TIMESTAMP
);

-- Crear tabla works (trabajos académicos)
CREATE TABLE works (
    id TEXT PRIMARY KEY,
    doi TEXT,
    title TEXT,
    display_name TEXT,
    publication_year INTEGER,
    publication_date TEXT,
    type TEXT,
    cited_by_count INTEGER,
    is_retracted BOOLEAN,
    is_paratext BOOLEAN,
    host_venue TEXT
);

-- Crear tabla authors (autores)
CREATE TABLE authors (
    id TEXT PRIMARY KEY,
    orcid TEXT,
    display_name TEXT,
    display_name_alternatives TEXT,
    works_count INTEGER,
    cited_by_count INTEGER,
    last_known_institution TEXT,
    works_api_url TEXT,
    updated_date TIMESTAMP
);

-- Crear tabla institutions (instituciones)
CREATE TABLE institutions (
    id TEXT PRIMARY KEY,
    ror TEXT,
    display_name TEXT,
    country_code TEXT,
    type TEXT,
    homepage_url TEXT,
    image_url TEXT,
    image_thumbnail_url TEXT,
    display_name_acronyms TEXT,
    display_name_alternatives TEXT,
    works_count INTEGER,
    cited_by_count INTEGER,
    works_api_url TEXT,
    updated_date TIMESTAMP
);

-- Crear tabla venues (venues de publicación)
CREATE TABLE venues (
    id TEXT PRIMARY KEY,
    issn_l TEXT,
    issn TEXT,
    display_name TEXT,
    publisher TEXT,
    works_count INTEGER,
    cited_by_count INTEGER,
    is_oa BOOLEAN,
    is_in_doaj BOOLEAN,
    homepage_url TEXT,
    works_api_url TEXT,
    updated_date TIMESTAMP
);

-- ========================================
-- TABLAS DE RELACIONES
-- ========================================

-- Relación jerárquica de conceptos
CREATE TABLE concepts_ancestors (
    concept_id TEXT NOT NULL,
    ancestor_id TEXT NOT NULL,
    FOREIGN KEY (concept_id) REFERENCES concepts(id) ON DELETE CASCADE,
    FOREIGN KEY (ancestor_id) REFERENCES concepts(id) ON DELETE CASCADE
);

-- Conceptos relacionados
CREATE TABLE concepts_related_concepts (
    concept_id TEXT NOT NULL,
    related_concept_id TEXT NOT NULL,
    score FLOAT4,
    FOREIGN KEY (concept_id) REFERENCES concepts(id) ON DELETE CASCADE,
    FOREIGN KEY (related_concept_id) REFERENCES concepts(id) ON DELETE CASCADE
);

-- Relación trabajos-conceptos
CREATE TABLE works_concepts (
    work_id TEXT NOT NULL,
    concept_id TEXT NOT NULL,
    score FLOAT4,
    FOREIGN KEY (concept_id) REFERENCES concepts(id) ON DELETE CASCADE,
    FOREIGN KEY (work_id) REFERENCES works(id) ON DELETE CASCADE
);

-- Autoría de trabajos
CREATE TABLE works_authorships (
    work_id TEXT NOT NULL,
    author_position TEXT,
    author_id TEXT,
    institution_id TEXT,
    FOREIGN KEY (work_id) REFERENCES works(id) ON DELETE CASCADE,
    FOREIGN KEY (author_id) REFERENCES authors(id) ON DELETE SET NULL,
    FOREIGN KEY (institution_id) REFERENCES institutions(id) ON DELETE SET NULL
);

-- Trabajos relacionados
CREATE TABLE works_related_works (
    work_id TEXT NOT NULL,
    related_work_id TEXT NOT NULL,
    FOREIGN KEY (work_id) REFERENCES works(id) ON DELETE CASCADE,
    FOREIGN KEY (related_work_id) REFERENCES works(id) ON DELETE CASCADE
);

-- Trabajos referenciados
CREATE TABLE works_referenced_works (
    work_id TEXT NOT NULL,
    referenced_work_id TEXT NOT NULL,
    FOREIGN KEY (work_id) REFERENCES works(id) ON DELETE CASCADE,
    FOREIGN KEY (referenced_work_id) REFERENCES works(id) ON DELETE CASCADE
);

-- Instituciones asociadas
CREATE TABLE institutions_associated_institutions (
    institution_id TEXT NOT NULL,
    associated_institution_id TEXT NOT NULL,
    relationship TEXT,
    FOREIGN KEY (institution_id) REFERENCES institutions(id) ON DELETE CASCADE,
    FOREIGN KEY (associated_institution_id) REFERENCES institutions(id) ON DELETE CASCADE
);

-- Venues alternativos para trabajos
CREATE TABLE works_alternate_host_venues (
    work_id TEXT NOT NULL,
    venue_id TEXT NOT NULL,
    FOREIGN KEY (work_id) REFERENCES works(id) ON DELETE CASCADE,
    FOREIGN KEY (venue_id) REFERENCES venues(id) ON DELETE CASCADE
);

-- Información bibliográfica de trabajos
CREATE TABLE works_biblio (
    work_id TEXT PRIMARY KEY,
    volume TEXT,
    issue TEXT,
    first_page TEXT,
    last_page TEXT,
    FOREIGN KEY (work_id) REFERENCES works(id) ON DELETE CASCADE
);

-- Información de mesh para trabajos
CREATE TABLE works_mesh (
    work_id TEXT NOT NULL,
    descriptor_ui TEXT,
    descriptor_name TEXT,
    qualifier_ui TEXT,
    qualifier_name TEXT,
    FOREIGN KEY (work_id) REFERENCES works(id) ON DELETE CASCADE
);

-- Acceso abierto de trabajos
CREATE TABLE works_open_access (
    work_id TEXT PRIMARY KEY,
    is_oa BOOLEAN,
    oa_status TEXT,
    oa_url TEXT,
    FOREIGN KEY (work_id) REFERENCES works(id) ON DELETE CASCADE
);

-- ========================================
-- TABLAS DE IDENTIFICADORES
-- ========================================

-- Identificadores de conceptos
CREATE TABLE concepts_ids (
    concept_id TEXT PRIMARY KEY,
    openalex TEXT,
    wikidata TEXT,
    wikipedia TEXT,
    umls_aui TEXT,
    umls_cui TEXT,
    mag INTEGER,
    FOREIGN KEY (concept_id) REFERENCES concepts(id) ON DELETE CASCADE
);

-- Identificadores de trabajos
CREATE TABLE works_ids (
    work_id TEXT PRIMARY KEY,
    openalex TEXT,
    doi TEXT,
    mag INTEGER,
    pmid TEXT,
    FOREIGN KEY (work_id) REFERENCES works(id) ON DELETE CASCADE
);

-- Identificadores de autores
CREATE TABLE authors_ids (
    author_id TEXT PRIMARY KEY,
    openalex TEXT,
    orcid TEXT,
    scopus TEXT,
    twitter TEXT,
    wikipedia TEXT,
    mag INTEGER,
    FOREIGN KEY (author_id) REFERENCES authors(id) ON DELETE CASCADE
);

-- Identificadores de venues
CREATE TABLE venues_ids (
    venue_id TEXT PRIMARY KEY,
    openalex TEXT,
    issn_l TEXT,
    issn TEXT,
    mag INTEGER,
    FOREIGN KEY (venue_id) REFERENCES venues(id) ON DELETE CASCADE
);

-- Identificadores de instituciones
CREATE TABLE institutions_ids (
    institution_id TEXT PRIMARY KEY,
    openalex TEXT,
    ror TEXT,
    grid TEXT,
    wikipedia TEXT,
    wikidata TEXT,
    mag INTEGER,
    FOREIGN KEY (institution_id) REFERENCES institutions(id) ON DELETE CASCADE
);

-- ========================================
-- TABLAS DE CONTEOS POR AÑO
-- ========================================

-- Conteos anuales de conceptos
CREATE TABLE concepts_counts_by_year (
    concept_id TEXT NOT NULL,
    year INTEGER NOT NULL,
    works_count INTEGER,
    cited_by_count INTEGER,
    PRIMARY KEY (concept_id, year),
    FOREIGN KEY (concept_id) REFERENCES concepts(id) ON DELETE CASCADE
);

-- Conteos anuales de autores
CREATE TABLE authors_counts_by_year (
    author_id TEXT NOT NULL,
    year INTEGER NOT NULL,
    works_count INTEGER,
    cited_by_count INTEGER,
    PRIMARY KEY (author_id, year),
    FOREIGN KEY (author_id) REFERENCES authors(id) ON DELETE CASCADE
);

-- Conteos anuales de venues
CREATE TABLE venues_counts_by_year (
    venue_id TEXT NOT NULL,
    year INTEGER NOT NULL,
    works_count INTEGER,
    cited_by_count INTEGER,
    PRIMARY KEY (venue_id, year),
    FOREIGN KEY (venue_id) REFERENCES venues(id) ON DELETE CASCADE
);

-- Conteos anuales de instituciones
CREATE TABLE institutions_counts_by_year (
    institution_id TEXT NOT NULL,
    year INTEGER NOT NULL,
    works_count INTEGER,
    cited_by_count INTEGER,
    PRIMARY KEY (institution_id, year),
    FOREIGN KEY (institution_id) REFERENCES institutions(id) ON DELETE CASCADE
);

-- ========================================
-- TABLAS DE INFORMACIÓN GEOGRÁFICA
-- ========================================

-- Información geográfica de instituciones
CREATE TABLE institutions_geo (
    institution_id TEXT PRIMARY KEY,
    city TEXT,
    geonames_city_id TEXT,
    region TEXT,
    country_code TEXT,
    country TEXT,
    latitude FLOAT4,
    longitude FLOAT4,
    FOREIGN KEY (institution_id) REFERENCES institutions(id) ON DELETE CASCADE
);
