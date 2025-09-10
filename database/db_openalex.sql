-- Creamos el esquema
CREATE SCHEMA IF NOT EXISTS openalex;

------ Entities --------
CREATE TABLE works (
    id TEXT PRIMARY KEY,
    doi TEXT,
    title TEXT,
    display_name TEXT,
    publication_year INTEGER,
    publication_date DATE,
    type TEXT,
    source_id TEXT,
    FOREIGN KEY (source_id) REFERENCES sources(id)
);

CREATE TABLE authors (
    id TEXT PRIMARY KEY,
    orcid TEXT,
    display_name TEXT,
    display_name_alternatives TEXT[],
    last_known_institution_id TEXT,
    FOREIGN KEY (last_known_institution_id) REFERENCES institutions(id)
);

CREATE TABLE sources (
    id TEXT PRIMARY KEY,
    issn TEXT[],
    display_name TEXT,
    publisher TEXT,
    alternate_names TEXT[]
);

CREATE TABLE institutions (
    id TEXT PRIMARY KEY,
    ror TEXT,
    display_name TEXT,
    country_code TEXT,
    type TEXT,
    works_count INTEGER,
    image_url TEXT,
    homepage_url TEXT
);

CREATE TABLE topics (
    id TEXT PRIMARY KEY,
    display_name TEXT,
    description TEXT,
    keywords TEXT[],
    subfield_id INTEGER,
    field_id INTEGER,
    domain_id INTEGER,
    works_count INTEGER,
    FOREIGN KEY (subfield_id) REFERENCES subfields(id),
    FOREIGN KEY (field_id) REFERENCES fields(id),
    FOREIGN KEY (domain_id) REFERENCES domains(id)
);


CREATE TABLE domains (
    id INTEGER PRIMARY KEY,
    display_name TEXT,
    description TEXT
);

CREATE TABLE fields (
    id INTEGER PRIMARY KEY,
    display_name TEXT,
    description TEXT,
    display_name_alternatives TEXT[],
    domain_id INTEGER NOT NULL,
    FOREIGN KEY (domain_id) REFERENCES domains(id)
);

CREATE TABLE subfields (
    id INTEGER PRIMARY KEY,
    display_name TEXT,
    description TEXT,
    display_name_alternatives TEXT[],
    field_id INTEGER NOT NULL,
    domain_id INTEGER NOT NULL,
    FOREIGN KEY (field_id) REFERENCES fields(id),
    FOREIGN KEY (domain_id) REFERENCES domains(id)
);


--------- counts -----------

CREATE TABLE authors_counts_by_year (
    author_id TEXT NOT NULL,
    year INTEGER NOT NULL,
    works_count INTEGER,
    PRIMARY KEY (author_id, year),
    FOREIGN KEY (author_id) REFERENCES authors(id)
);

CREATE TABLE source_counts_by_year (
    source_id TEXT NOT NULL,
    year INTEGER NOT NULL,
    works_count INTEGER,
    PRIMARY KEY (source_id, year),
    FOREIGN KEY (source_id) REFERENCES sources(id)
);

CREATE TABLE institutions_counts_by_year (
    institution_id TEXT NOT NULL,
    year INTEGER NOT NULL,
    works_count INTEGER,
    PRIMARY KEY (institution_id, year),
    FOREIGN KEY (institution_id) REFERENCES institutions(id)
);

---------- join tables ---------

CREATE TABLE works_topics (
    work_id TEXT NOT NULL,
    topic_id TEXT NOT NULL,
    PRIMARY KEY (work_id, topic_id),
    FOREIGN KEY (work_id) REFERENCES works(id),
    FOREIGN KEY (topic_id) REFERENCES topics(id)
);

CREATE TABLE works_authorships (
    work_id TEXT NOT NULL,
    author_id TEXT NOT NULL,
    author_position INTEGER,
    institution_id TEXT,
    PRIMARY KEY (work_id, author_id),
    FOREIGN KEY (work_id) REFERENCES works(id),
    FOREIGN KEY (author_id) REFERENCES authors(id),
    FOREIGN KEY (institution_id) REFERENCES institutions(id)
);

