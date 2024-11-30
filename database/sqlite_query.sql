-- Create the database (SQLite does not use this command; simply connect to the database file)
-- CREATE DATABASE pharmacie;

-- Create the catalogue table
CREATE TABLE catalogue(
    fournisseur TEXT,
    libelle TEXT,
    PU DECIMAL(15, 4),
    TVA INTEGER,
    date_peremption DATE
);

-- Create the fournisseur table
CREATE TABLE fournisseur(
    id INTEGER PRIMARY KEY AUTOINCREMENT, -- SQLite uses AUTOINCREMENT for serial-like functionality
    nom TEXT UNIQUE
);

-- Create the view for best quality product by expiration date
CREATE VIEW v_best_quality_product AS   
    SELECT * FROM catalogue ORDER BY date_peremption DESC; 

-- Create the view for best quality price ratio product
CREATE VIEW v_best_quality_price_ratio_product AS   
    SELECT * FROM v_best_quality_product ORDER BY pu ASC;

-- Since SQLite doesn't support stored procedures, we can implement the logic directly in code or use a trigger.
-- Here's how you can do the insert operation as a standalone query:
INSERT INTO fournisseur(nom)
    SELECT DISTINCT fournisseur 
    FROM catalogue
    WHERE NOT EXISTS (
        SELECT 1 FROM fournisseur WHERE fournisseur.nom = catalogue.fournisseur
    );

-- SQLite does not have the COPY command, so to load data from a CSV file you can use the .import command:
-- Assuming you're running this in the SQLite command-line shell:
-- .mode csv
-- .import E:/PHARMACIE/Triage/uploads/CATALOGUES_120824.csv catalogue
