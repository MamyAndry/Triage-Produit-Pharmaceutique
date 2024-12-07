CREATE OR REPLACE VIEW v_best_quality_product AS   
    SELECT * FROM catalogue ORDER BY date_peremption DESC; 

CREATE OR REPLACE VIEW v_best_quality_price_ratio_product AS   
    SELECT * FROM v_best_quality_product ORDER BY pu ASC; 

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

CREATE OR REPLACE VIEW v_fournisseur_classement_lib AS
    SELECT 
        rang.id,
        frns.nom,
        rang.classement
        FROM fournisseur frns
            JOIN fournisseur_classement rang
                ON rang.id_fournisseur = frns.id
        ORDER BY rang.classement ASC;