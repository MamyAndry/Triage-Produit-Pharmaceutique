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

CREATE TABLE fournisseur_classement(
    id SERIAL,
    classement INTEGER,
    id_fournisseur INTEGER,
    FOREIGN KEY(id_fournisseur) REFERENCES fournisseur(id)
);

ALTER TABLE catalogue ADD catalogue_search tsvector NULL;
ALTER TABLE catalogue ALTER COLUMN TVA TYPE VARCHAR(50) USING TVA::VARCHAR(50) CASCADE;
ALTER TABLE fournisseur ADD CONSTRAINT primary_key_fournisseur PRIMARY KEY(id);

SELECT * FROM catalogue WHERE catalogue_search @@ to_tsquery('french', 'paracetamol&500MG&SOPHARMAD&2025'); 