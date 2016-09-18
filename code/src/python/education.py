

import json
from college_info_trie import possible_college_search
from dao import Dao
import pandas as pd

from constant import (FAILED_EDUCATION_JSON_PARSE)
from utility import Utility

import traceback
import re

def check_if_year(input_string):
    year_list = list()
    word_list = input_string.split(" ")
    words_hyphen_split = list() 
    for word in word_list:
        for w in word.split("-"):
            w = w.strip()
            match = re.search(r'\d+',w)
            if match:
                val = match.group(0)
                if int(val) > 1800 and int(val) < 2050:
                    year_list.append(int(val))
    if year_list:
        if len(year_list) > 1:
            return (year_list[0], year_list[1])
        else:
            return (None, year_list[0])
    return (None, None)


DEGREE_META_DATA = ['ph.d.', 'ph.d', 'phd', 'doctor of philosophy', 'doctor'
    ,'m.s.', 'm.s', 'ms', 'm.a.', 'm.a', 'ma', 'master'
    ,'m.b.a.', 'm.b.a', 'mba'
    ,'b.s.', 'b.s', 'bs',  'bachelor'
    ,'b.a.', 'b.a', 'ba'
    ,'minor']

def check_for_degree(input_string):
    if input_string in DEGREE_META_DATA:
        return input_string

    split_val = input_string.split()
    for val in split_val:
        if val in DEGREE_META_DATA:
            return val

NOISE_WORDS = ['economics', 'business', 'management', 'university', 'graduate', "education", "administration"]
#NOISE_WORDS = []

def remove_noise_words(input_string):
    if input_string in NOISE_WORDS:
        return ' '
    return input_string

    """
    new_input_string = list()
    split_val = input_string.split()
    for val in split_val:
        if val not in NOISE_WORDS:
            new_input_string.append(val)
    return ' '.join(new_input_string)
    """

def education_parsing(word_list, file_name, is_forward=1):
    column = {'start_year': None, 'end_year': None, 'degree': None, 'college': None}
    row = list()
    unprocessed_string = list()
    found_college = False
    found_year = False  
    found_degree = False
    
    for words_pipe_split in word_list:
        for words in words_pipe_split.split(","):
            input_string = str(words.strip()).lower()
            original_input_string = input_string
            
            input_string = remove_noise_words(input_string)
            if not input_string:
                continue
            
            # Check for year
            (start, end) = check_if_year(input_string)
            if end:
                if found_year:
                    column['file_name'] = file_name
                    column['is_forward'] = is_forward
                    row.append(dict(column))
                    column = dict()
                    found_college = False
                    found_year = False  
                    found_degree = False
                if start:
                    column['start_year'] = start
                    input_string = input_string.replace(str(start), '')
                column['end_year'] = end
                found_year = True            
                input_string = input_string.replace(str(end), '')
            if not input_string:
                continue

            # Check for degree
            degree = check_for_degree(input_string)
            if degree:
                if found_degree:
                    column['file_name'] = file_name
                    column['is_forward'] = is_forward
                    row.append(dict(column))
                    column = dict()
                    found_college = False
                    found_year = False  
                    found_degree = False
                column['degree'] = degree
                found_degree = True
                input_string = input_string.replace(degree, '')
            if not input_string:
                continue

            # Check for college
            college_possible = possible_college_search(input_string)
            if college_possible:
                if found_college:
                    column['file_name'] = file_name
                    column['is_forward'] = is_forward
                    row.append(dict(column))
                    column = dict()
                    found_college = False
                    found_year = False  
                    found_degree = False
                column['college'] = original_input_string
                found_college = True

                for val in original_input_string.split(" "):
                    input_string = input_string.replace(val, '')
            if not input_string:
                continue

            #if not (found_college or found_year or found_degree):
            if input_string:
                unprocessed_string.append(input_string)
    unprocessed = ' '.join(unprocessed_string)
    if len(unprocessed) > 6000:
        unprocessed = unprocessed[:6000]
    if column and ('college' in column and column['college'] or
                   'end_year' in column and column['end_year'] or
                   'degree' in column and column['degree']):
        column['file_name'] = file_name
        column['is_forward'] = is_forward
        row.append(column)
    unprocessed = [{'file_name': file_name, 'unprocessed': unprocessed,
        'is_forward': is_forward}]
    return (row, unprocessed)

def convert_to_df(data_list):
    df = pd.DataFrame(data_list)
    df_clean = df.where((pd.notnull(df)), None)
    return df_clean

def put_parse_data_to_db(forward_parse, reverse_parse,
                         forward_unparsed, reverse_unparsed):
    dao = Dao()
    dao.insert_education_raw(forward_parse)
    dao.insert_education_raw(reverse_parse)
    dao.insert_education_unprocessed(forward_unparsed)
    dao.insert_education_unprocessed(reverse_unparsed)

def compare_diff_of_forward_reverse_parse(forward_parse, reverse_parse):
    df = pd.concat([forward_parse, reverse_parse])
    df = df.reset_index(drop=True)
    df = df.drop('is_forward', 1)
    diff_rows = df.groupby(list(df.columns))
    diff_df_rows = [x[0] for x in diff_rows.groups.values() if len(x) == 1]
    

def categorize_education_info(edu_json_path):
    utility = Utility()
    education_info = utility.read_from_json(edu_json_path)
    education_error_files = list()
    forward_parse_result = list()
    reverse_parse_result = list()
    forward_unparsed = list()
    reverse_unparsed = list()
    for cv in education_info:
        try:
            education_content = str(cv["education"])
            file_name = str(cv["file_name"])
            
            word_list = education_content.split("|")
            (forward_processed, forward_unprocessed) = education_parsing(word_list, file_name)
            if not forward_processed:
                raise Exception("No data parsed from education ********************")
            word_list.reverse()
            (reverse_processed, reverse_unprocessed) = education_parsing(word_list, file_name, is_forward=0)

            forward_parse_result.extend(forward_processed)
            reverse_parse_result.extend(reverse_processed)
            forward_unparsed.extend(forward_unprocessed)
            reverse_unparsed.extend(reverse_unprocessed)
        except Exception, e:
            print traceback.print_exc()
            err_file_name = edu_json_path
            if cv and file_name in cv:
                err_file_name = cv['file_name']
            education_error_files.append(err_file_name)
    
    if education_error_files:
        utility = Utility()
        error_files_string = '","'.join(education_error_files)
        utility.write_to_text_file(FAILED_EDUCATION_JSON_PARSE, error_files_string)

    forward_parse = convert_to_df(forward_parse_result)
    reverse_parse = convert_to_df(reverse_parse_result)
    forward_unparsed = convert_to_df(forward_unparsed)
    reverse_unparsed = convert_to_df(reverse_unparsed)
    put_parse_data_to_db(forward_parse, reverse_parse, forward_unparsed, reverse_unparsed)
    
    #compare_diff_of_forward_reverse_parse(forward_parse, reverse_parse)

