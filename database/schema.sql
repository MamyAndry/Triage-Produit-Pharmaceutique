CREATE DATABASE pharmacie;

\c pharmacie

CREATE TABLE catalogue(
    fournisseur VARCHAR(255),
    libelle VARCHAR(255),
    PU DECIMAL(15, 4),
    TVA INTEGER,
    date_peremption DATE
);