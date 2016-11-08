-- %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
-- Creating cv_parsing database
-- %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

-- DROP DATABASE cv_parsing
CREATE DATABASE cv_parsing;

USE cv_parsing;

-- %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
-- Creating the tables
-- %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

-- DROP TABLE cv_parsing.education_raw
-- DELETE FROM cv_parsing.education_raw
CREATE TABLE cv_parsing.education_raw (
    id int NOT NULL AUTO_INCREMENT,
    file_name varchar(512),
    start_year int,
    end_year int,
    degree varchar(255),
    matched_college varchar(512),
    row_info varchar(8000),    
    logic_code int,
    row_counts int,
    is_college_propogated int,
    manual_check int,
    Primary KEY(id)
);

ALTER TABLE cv_parsing.education_unprocessed MODIFY COLUMN unprocessed VARCHAR(8000)  
    CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL;

-- DROP TABLE cv_parsing.work_raw
CREATE TABLE cv_parsing.work_raw (
	id int NOT NULL AUTO_INCREMENT,
    file_name varchar(512),
    start_year int,
    end_year int,
    title varchar(255),
    matched_college varchar(512),
    row_info varchar(8000),    
    category_info int,
    logic_code int,
    row_counts int,
    is_college_propogated int,
    manual_check int,
    Primary KEY(id)
);

ALTER TABLE cv_parsing.work_raw MODIFY COLUMN row_info VARCHAR(8000)  
    CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL;

-- %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
-- Queries to find exception cases between 
-- Learning Agent and Normal parsing
-- %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

SELECT *
FROM cv_parsing.work_raw w1
	INNER JOIN cv_parsing.work_raw w2 ON w1.file_name = w2.file_name AND w1.row_counts = w2.row_counts
		AND w2.logic_code = 3 AND w1.logic_code = 1
WHERE w1.start_year != w2.start_year 
	OR w1.end_year != w2.end_year 
	OR w1.title != w2.title 
    OR w1.matched_college != w2.matched_college;
    
SELECT *
FROM cv_parsing.work_raw w1
	INNER JOIN cv_parsing.work_raw w2 ON w1.file_name = w2.file_name AND w1.row_counts = w2.row_counts
		AND w2.logic_code = 4 AND w1.logic_code = 2
WHERE w1.start_year != w2.start_year 
	OR w1.end_year != w2.end_year 
	OR w1.title != w2.title 
    OR w1.matched_college != w2.matched_college;


-- %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
-- Other important queries
-- %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

/*
UPDATE mysql.user
    SET authentication_string = PASSWORD('cv_parsing'), password_expired = 'N'
    WHERE User = 'root' AND Host = 'localhost';
FLUSH PRIVILEGES;


SET PASSWORD FOR root@localhost=PASSWORD('');

#INSERT INTO cv_parsing.education_raw (file_name, start_year, end_year, college, is_forward) 
# 	VALUES ('sunil.pdf', 2016, 2018, 'USC', 1);
*/

-- %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
-- Unused queries
-- %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

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

-- *****************************************
-- Work related select query
-- *****************************************

SELECT * FROM cv_parsing.work_raw WHERE file_name = "1007.pdf"

SELECT * FROM cv_parsing.work_raw WHERE logic_code = 1

DELETE FROM cv_parsing.work_raw

SELECT * 
FROM cv_parsing.work_raw 
WHERE logic_code = 1

SELECT * 
FROM cv_parsing.work_raw 
WHERE file_name = '4618.pdf'
ORDER BY logic_code

SELECT w1.row_counts, w1.title, w2.title
FROM cv_parsing.work_raw w1
	INNER JOIN cv_parsing.work_raw w2 ON w1.file_name = w2.file_name AND w1.row_counts = w2.row_counts
		AND w2.logic_code = 3 AND w1.logic_code = 1
WHERE w1.title != w2.title


-- *****************************************
-- Education related select query
-- *****************************************
DELETE FROM cv_parsing.education_raw;

SELECT * FROM cv_parsing.education_raw 
WHERE file_name = '1004.pdf';

-- 1360
SELECT count(distinct file_name) FROM cv_parsing.education_raw  WHERE logic_code = 2;




ALTER TABLE cv_parsing.work_raw
	ADD manual_check int


UPDATE business AS b
INNER JOIN business_geocode AS g ON b.business_id = g.business_id
SET b.mapx = g.latitude,
  b.mapy = g.longitude
WHERE  (b.mapx = '' or b.mapx = 0) and
  g.latitude > 0


UPDATE cv_parsing.work_raw w1
INNER JOIN cv_parsing.work_raw w2 ON w1.file_name = w2.file_name AND w1.row_counts = w2.row_counts
		AND w2.logic_code = 3 AND w1.logic_code = 1
SET w1.manual_check = 1
WHERE w1.start_year != w2.start_year 
	OR w1.end_year != w2.end_year 
	OR w1.title != w2.title 
    OR w1.matched_college != w2.matched_college;
    
UPDATE cv_parsing.work_raw w1
INNER JOIN cv_parsing.work_raw w2 ON w1.file_name = w2.file_name AND w1.row_counts = w2.row_counts
		AND w2.logic_code = 4 AND w1.logic_code = 2
SET w1.manual_check = 1
WHERE w1.start_year != w2.start_year 
	OR w1.end_year != w2.end_year 
	OR w1.title != w2.title 
    OR w1.matched_college != w2.matched_college;
    

SELECT * FROM cv_parsing.work_raw
WHERE manual_check = 1 AND logic_code != 1


