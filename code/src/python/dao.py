"""
Data access object module is used for linking the service to the database.
All the insertion, selection & updation query related to the database are present here.
"""
import sys
import mysql.connector
import pandas as pd

class Dao(object):
    """
    Class used for talking to mysql database
    """
    def __init__(self):
        """
        Intializes the connection string object
        """
        self.cnx = mysql.connector.connect(user='root', database='cv_parsing',\
            host='127.0.0.1', port=3306, raise_on_warnings=True)

    def get_education_raw(self):
        """
        Query fetch the education table information. This currently not used
        """
        cursor = self.cnx.cursor()
        query = """
            SELECT * FROM cv_parsing.education_raw
        """
        row = list()
        cursor.execute(query)
        for (id_val, file_name, start_year, end_year, college) in cursor:
            result = dict()
            result['id'] = id_val
            result['file_name'] = file_name
            result['start_year'] = start_year
            result['end_year'] = end_year
            result['college'] = college
            row.append(result)
        return pd.DataFrame(row)

    def insert_education_raw(self, dframe):
        """
        This function inserts the parsed education information into the database
        """
        query = """
            INSERT INTO cv_parsing.education_raw (file_name, start_year, end_year, degree,\
                matched_college, row_info, logic_code, row_counts,\
                is_college_propogated, manual_check) 
            VALUES ('%s', %s, %s, '%s', '%s', '%s', %s, %s, %s, %s)
        """
        dframe = dframe.replace({"\'": '\\\''}, regex=True)

        for row in dframe.iterrows():
            cursor = self.cnx.cursor()
            query_str = query %(row[1]['file_name'],\
                                row[1]['start_year'] if row[1]['start_year'] else 0,
                                row[1]['end_year'] if row[1]['end_year'] else 0,
                                row[1]['degree'] if row[1]['degree'] else 'NULL',
                                row[1]['matched_college'] if row[1]['matched_college'] else 'NULL',
                                row[1]['row_info'] if row[1]['row_info'] else 'NULL',
                                row[1]['logic_code'],
                                row[1]['row_counts'],
                                row[1]['is_college_propogated'],
                                0)
            cursor.execute(query_str.encode(sys.stdout.encoding, errors='replace'))
            self.cnx.commit()
            cursor.close()

    def insert_work_raw(self, dframe):
        """
        This function inserts the parsed work related information into the database
        """
        query = """
            INSERT INTO cv_parsing.work_raw (file_name, start_year, end_year, title,\
                matched_college, row_info, category_info, logic_code, row_counts,\
                is_college_propogated, manual_check) 
            VALUES ('%s', %s, %s, '%s', '%s', '%s', '%s', %s, %s, %s, %s)
        """
        dframe = dframe.replace({"\'": '\\\''}, regex=True)

        for row in dframe.iterrows():
            cursor = self.cnx.cursor()
            query_str = query %(row[1]['file_name'],
                                row[1]['start_year'] if row[1]['start_year'] else 0,
                                row[1]['end_year'] if row[1]['end_year'] else 0,
                                row[1]['title'] if row[1]['title'] else 'NULL',
                                row[1]['matched_college'] if row[1]['matched_college'] else 'NULL',
                                row[1]['row_info'] if row[1]['row_info'] else 'NULL',
                                row[1]['category_info'] if row[1]['category_info'] else 0,
                                row[1]['logic_code'],
                                row[1]['row_counts'],
                                row[1]['is_college_propogated'],
                                0)
            cursor.execute(query_str.encode(sys.stdout.encoding, errors='replace'))
            self.cnx.commit()
            cursor.close()

    def update_manual_check_education(self, learning_logic_code, plain_logic_code):
        """
        Once the learning agent parsed data & the plain parsing data are inserted in the database.
        A query is run to update manual_check column to identify the mismatch in both parsing.
        """
        cursor = self.cnx.cursor()
        query_str = """
            UPDATE cv_parsing.education_raw e1
            INNER JOIN cv_parsing.education_raw e2 ON e1.file_name = e2.file_name AND e1.row_counts = e2.row_counts
                    AND e1.logic_code = %(learning_logic_code)s AND e2.logic_code = %(plain_logic_code)s
            SET e1.manual_check = 1
            WHERE e1.start_year != e2.start_year 
                OR e1.end_year != e2.end_year 
                OR e1.degree != e2.degree 
                OR e1.matched_college != e2.matched_college
        """ %{'learning_logic_code': learning_logic_code, 'plain_logic_code': plain_logic_code}
        cursor.execute(query_str.encode(sys.stdout.encoding, errors='replace'))
        self.cnx.commit()
        cursor.close()

    def update_manual_check_work(self, learning_logic_code, plain_logic_code):
        """
        Once the learning agent parsed data & the plain parsing data are inserted in the database.
        A query is run to update manual_check column to identify the mismatch in both parsing.
        """
        cursor = self.cnx.cursor()
        query_str = """
            UPDATE cv_parsing.work_raw w1
            INNER JOIN cv_parsing.work_raw w2 ON w1.file_name = w2.file_name AND w1.row_counts = w2.row_counts
                    AND w1.logic_code = %(learning_logic_code)s AND w2.logic_code = %(plain_logic_code)s
            SET w1.manual_check = 1
            WHERE w1.start_year != w2.start_year 
                OR w1.end_year != w2.end_year 
                OR w1.title != w2.title 
                OR w1.matched_college != w2.matched_college
        """ %{'learning_logic_code': learning_logic_code, 'plain_logic_code': plain_logic_code}
        cursor.execute(query_str.encode(sys.stdout.encoding, errors='replace'))
        self.cnx.commit()
        cursor.close()
