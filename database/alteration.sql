DROP VIEW v_best_quality_price_ratio_product;
DROP VIEW v_best_quality_product;

ALTER TABLE catalogue ALTER COLUMN TVA TYPE VARCHAR(50) USING TVA::VARCHAR(50) CASCADE;

CREATE OR REPLACE VIEW v_best_quality_product AS   
    SELECT * FROM catalogue ORDER BY date_peremption DESC; 

CREATE OR REPLACE VIEW v_best_quality_price_ratio_product AS   
    SELECT * FROM v_best_quality_product ORDER BY pu ASC; 

ALTER TABLE fournisseur ADD CONSTRAINT primary_key_fournisseur PRIMARY KEY(id);

CREATE TABLE fournisseur_classement(
    id SERIAL PRIMARY KEY,
    classement INTEGER DEFAULT 1,
    id_fournisseur INTEGER,
    FOREIGN KEY(id_fournisseur) REFERENCES fournisseur(id)
);

CREATE OR REPLACE PROCEDURE p_entree_fournisseur_nom()
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO fournisseur(nom)
    SELECT DISTINCT fournisseur 
    FROM catalogue
    ON CONFLICT (nom) DO NOTHING;
END
$$;

CREATE OR REPLACE PROCEDURE p_entree_fournisseur_classement()
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO fournisseur_classement(id_fournisseur)
    SELECT id 
    FROM fournisseur
    ON CONFLICT DO NOTHING;
END
$$;

CREATE OR REPLACE PROCEDURE p_entree_fournisseur()
LANGUAGE plpgsql
AS $$
BEGIN
    CALL p_entree_fournisseur_nom();
    CALL p_entree_fournisseur_classement();
END
$$;

CREATE OR REPLACE VIEW v_best_quality_price_ratio_product_by_frns AS
    SELECT 
        rapport.fournisseur,
        rapport.libelle,
        rapport.PU,
        rapport.TVA,
        rapport.date_peremption 
        FROM v_best_quality_price_ratio_product rapport
                JOIN fournisseur frns
                    ON frns.nom = rapport.fournisseur 
                JOIN fournisseur_classement rang
                    ON rang.id_fournisseur = frns.id
        ORDER BY rang.classement ASC;