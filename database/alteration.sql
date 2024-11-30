DROP VIEW v_best_quality_price_ratio_product;
DROP VIEW v_best_quality_product;

ALTER TABLE catalogue ALTER COLUMN TVA TYPE VARCHAR(50) USING TVA::VARCHAR(50) CASCADE;

CREATE OR REPLACE VIEW v_best_quality_product AS   
    SELECT * FROM catalogue ORDER BY date_peremption DESC; 

CREATE OR REPLACE VIEW v_best_quality_price_ratio_product AS   
    SELECT * FROM v_best_quality_product ORDER BY pu ASC; 

ALTER TABLE fournisseur ADD CONSTRAINT primary_key_fournisseur PRIMARY KEY(id);

CREATE TABLE fournisseur_classement(
    id SERIAL,
    classement INTEGER,
    id_fournisseur INTEGER,
    FOREIGN KEY(id_fournisseur) REFERENCES fournisseur(id)
);