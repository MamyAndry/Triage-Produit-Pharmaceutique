CREATE PROCEDURE p_update()
LANGUAGE plpgsql
AS $$
    BEGIN
        UPDATE catalogue SET catalogue_search = to_tsvector(
            'french', 
            fournisseur || ' ' ||
            libelle || ' ' ||
            PU || ' ' ||
            date_peremption
        ); 
    END
$$;

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
