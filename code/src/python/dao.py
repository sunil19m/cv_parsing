import datetime
import mysql.connector
import pandas as pd
import sys


class Dao(object):
    def __init__(self):
        self.cnx = mysql.connector.connect(user='root',
            database='cv_parsing',
            host='127.0.0.1',
            port=3306,
            raise_on_warnings=True)     

    def get_education_raw(self):        
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

    def insert_education_raw(self, df):
        query = """
            INSERT INTO cv_parsing.education_raw (file_name, start_year, end_year, degree,\
                cv_college, matched_college, education_content, logic_code) 
            VALUES ('%s', %s, %s, '%s', '%s', '%s', '%s', %s)
        """
        df = df.replace({"\'": '\\\''}, regex=True)

        for row in df.iterrows():
            cursor = self.cnx.cursor()
            query_str = query %(row[1]['file_name'],
                            row[1]['start_year'] if row[1]['start_year'] else 0,
                            row[1]['end_year'] if row[1]['end_year'] else 0,
                            row[1]['degree'] if row[1]['degree'] else 'NULL',
                            row[1]['cv_college'] if row[1]['cv_college'] else 'NULL',
                            row[1]['matched_college'] if row[1]['matched_college'] else 'NULL',
                            row[1]['education_content'] if row[1]['education_content'] else 'NULL',
                            row[1]['logic_code']
                        )
            cursor.execute(query_str.encode(sys.stdout.encoding, errors='replace'))
            self.cnx.commit()
            cursor.close()
        

