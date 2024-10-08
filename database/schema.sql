CREATE DATABASE pharmacie;

\c pharmacie

CREATE TABLE catalogue(
    fournisseur VARCHAR(255),
    libelle VARCHAR(255),
    PU DECIMAL(15, 
    4),
    TVA INTEGER,
    date_peremption DATE
);

CREATE TABLE fournisseur(
    id SERIAL,
    nom VARCHAR(50),
    UNIQUE(nom)
);

ALTER TABLE catalogue ADD catalogue_search tsvector NULL;


SELECT * FROM catalogue WHERE catalogue_search @@ to_tsquery('french', 'paracetamol&500MG&SOPHARMAD&2025'); 