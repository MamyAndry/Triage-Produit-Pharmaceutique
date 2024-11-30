CREATE OR REPLACE VIEW v_best_quality_product AS   
    SELECT * FROM catalogue ORDER BY date_peremption DESC; 

CREATE OR REPLACE VIEW v_best_quality_price_ratio_product AS   
    SELECT * FROM v_best_quality_product ORDER BY pu ASC; 