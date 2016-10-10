-- DROP DATABASE cv_parsing
CREATE DATABASE cv_parsing;

USE cv_parsing;


-- DROP TABLE cv_parsing.education_raw
-- DELETE FROM cv_parsing.education_raw
CREATE TABLE cv_parsing.education_raw (
	id int NOT NULL AUTO_INCREMENT,
    file_name varchar(512),
    start_year int,
    end_year int,
    degree varchar(255),
    cv_college varchar(512),
    matched_college varchar(512),
    education_content varchar(8000),
    logic_code int,
    Primary KEY(id)
);


ALTER TABLE cv_parsing.education_unprocessed MODIFY COLUMN unprocessed VARCHAR(8000)  
    CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL;




 

SELECT * FROM cv_parsing.education_raw
WHERE file_name = "2056.pdf"

DELETE FROM cv_parsing.education_raw;

SELECT * FROM cv_parsing.education_raw 
WHERE logic_code = 2;


SELECT * FROM cv_parsing.education_unprocessed;
WHERE is_forward = 0


#INSERT INTO cv_parsing.education_raw (file_name, start_year, end_year, college, is_forward) 
# 	VALUES ('sunil.pdf', 2016, 2018, 'USC', 1);

/*
UPDATE mysql.user
    SET authentication_string = PASSWORD('cv_parsing'), password_expired = 'N'
    WHERE User = 'root' AND Host = 'localhost';
FLUSH PRIVILEGES;


SET PASSWORD FOR root@localhost=PASSWORD('');
*/

-- 1360
SELECT count(distinct file_name) FROM cv_parsing.education_raw  WHERE logic_code = 2;


-- Rows which require some attention
-- 138 Files
-- SELECT count(distinct file_name)
SELECT *  
FROM cv_parsing.education_raw e1 
WHERE e1.is_forward = 1 AND
	NOT EXISTS (
		SELECT 0
        FROM cv_parsing.education_raw e2 
        WHERE e2.file_name = e1.file_name AND e2.is_forward = 0
			AND (e2.start_year = e1.start_year or (e2.start_year is NULL AND e1.start_year is NULL))
            AND (e2.end_year = e1.end_year or (e2.end_year is NULL AND e1.end_year is NULL))
            AND (e2.college = e1.college or (e2.college is NULL AND e1.college is NULL))
) 
AND file_name = "664.pdf";


SELECT *  
FROM cv_parsing.education_raw e1 
WHERE e1.is_forward = 0 AND
	NOT EXISTS (
		SELECT 0
        FROM cv_parsing.education_raw e2 
        WHERE e2.file_name = e1.file_name AND e2.is_forward = 1
			AND (e2.start_year = e1.start_year or (e2.start_year is NULL AND e1.start_year is NULL))
            AND (e2.end_year = e1.end_year or (e2.end_year is NULL AND e1.end_year is NULL))
            AND (e2.college = e1.college or (e2.college is NULL AND e1.college is NULL))
) 
AND file_name = "664.pdf";



-- High quality pdfs data
-- 411
-- SELECT count(distinct file_name)
SELECT *  
FROM  cv_parsing.education_raw r
WHERE file_name NOT IN (
	SELECT distinct file_name
	FROM cv_parsing.education_raw e1 
	WHERE e1.is_forward = 1 AND
		NOT EXISTS (
			SELECT 0
			FROM cv_parsing.education_raw e2 
			WHERE e2.file_name = e1.file_name AND e2.is_forward = 0
				AND (e2.start_year = e1.start_year or (e2.start_year is NULL AND e1.start_year is NULL))
				AND (e2.end_year = e1.end_year or (e2.end_year is NULL AND e1.end_year is NULL))
				AND (e2.college = e1.college or (e2.college is NULL AND e1.college is NULL))
	) 
) AND r.is_forward = 1




