

import json
from college_info_trie import possible_college_search
from dao import Dao
import pandas as pd

from constant import (FAILED_EDUCATION_JSON_PARSE)
from utility import Utility

import traceback
import re


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

def add_to_row(row_data, column_data, found_category, file_name, education_content):
    #print "&&&&&&&&&&&&"
    #print column_data
    column_data['file_name'] = file_name
    column_data['education_content'] = education_content
    row_data.append(dict(column_data))
    column_data = dict()
    found_category['found_college'] = False
    found_category['found_year'] = False  
    found_category['found_degree'] = False
    return row_data, column_data, found_category


DEGREE_META_DATA = ['ph.d.', 'ph.d', 'phd', 'doctor'
    ,'m.s.', 'm.s', 'ms'
    ,'m.a.', 'm.a', 'ma', 'master'
    ,'m.b.a.', 'm.b.a', 'mba'
    ,'m.sc.', 'msc', 'm.s.c'
    ,'m.phil', 'm.phil.', 'mphil' 
    ,'b.s.', 'b.s', 'bs',  'bachelor'
    ,'b.a.', 'b.a', 'ba'
    ,'bbm', 'b.b.m', 'b.b.m.', 'bbm.'
    ,'bba', 'b.b.a', 'b.b.a.', 'bba.'
    ,'a.b.', 'a.b', 'ab'    
    ,'minor']

MORE_DEGREES = ['habilitation', 'general', 'licentiate', 'high']

ALL_DEGREES = DEGREE_META_DATA
ALL_DEGREES.extend(MORE_DEGREES)

def check_for_degree(input_string):
    if input_string in ALL_DEGREES:
        return input_string

def check_if_year(word):
    match = re.search(r'\d+',word)
    if match:
        val = match.group(0)
        if int(val) > 1800 and int(val) < 2050:
            return int(val)

def check_year_degree(input_string):
    found_year = False
    found_degree = False
    order_parse = list()
    result = dict()
    word_list = input_string.split(" ")
    word_list_comma = list()
    for x in word_list:
        word_list_comma.extend(x.split(","))

    year_list = list()
    for word in word_list_comma:
        w_split = word.split("-")
        for w in w_split:
            w = w.strip()
            
            year = check_if_year(w)
            if year:
                if not found_year:
                    order_parse.append("found_year")
                    found_year = True
                year_list.append(year)
                
            if not found_degree:
                degree = check_for_degree(w)
                if degree:
                    order_parse.append("found_degree")
                    result['degree'] = degree
                    found_degree = True

    if year_list:
        if len(year_list) > 1:
            result['end'] = year_list[1]
            result['start'] = year_list[0]
        else:
            result['end'] = year_list[0]
            result['start'] = None
    return (order_parse, result)

def check_learn_order(learn_order, found_category, category, input_string):
    rank = learn_order[category]
    for key, value in learn_order.iteritems():
        if value < rank:
            if key == "found_college":
                matched_college = possible_college_search(input_string)
                if matched_college:
                    continue
            found_category[key] = True
    return found_category

def education_parsing(word_list, file_name, education_content):
    education_content_db = education_content[:7000]

    column = {'start_year': None, 'end_year': None, 'degree': None,\
              'cv_college': None, 'matched_college': None, 'college_line': None}
    row = list()
    found_category = {'found_college': False, 'found_year': False, 'found_degree': False}

    unprocessed_string = list()
    
    learn_order = dict()
    count = 0
    for word in word_list:    
        input_string = str(word.strip()).lower()
        original_input_string = input_string

        input_string = remove_noise_words(input_string)
        if not input_string:
            continue

        #print input_string
        start = None
        end = None
        degree = None
        (order_category, year_degree_result) = check_year_degree(input_string)
        for idx, val in enumerate(order_category):
            if val == "found_year":
                start = year_degree_result["start"]
                end = year_degree_result["end"]

                if found_category['found_year']:  
                    row, column, found_category = add_to_row(row, column, found_category, file_name, education_content_db)
                if 'found_year' not in learn_order:
                    count = count + 1
                    learn_order['found_year'] = count
                else:
                    found_category = check_learn_order(learn_order, found_category, "found_year", input_string)
                if start:
                    column['start_year'] = start
                    input_string = input_string.replace(str(start), '')
                
                column['end_year'] = end
                found_category['found_year'] = True
                input_string = input_string.replace(str(end), '')
        
            elif val == "found_degree":
                degree = year_degree_result["degree"]
                if found_category['found_degree']:
                    row, column, found_category = add_to_row(row, column, found_category, file_name, education_content_db)
                if 'found_degree' not in learn_order:
                    count = count + 1
                    learn_order['found_degree'] = count
                else:
                    found_category = check_learn_order(learn_order, found_category, "found_degree", input_string)
                column['degree'] = degree                
                found_category['found_degree'] = True
                input_string = input_string.replace(degree, '')
        
        
        # Check for college
        matched_college = possible_college_search(input_string)
        if matched_college:
            if found_category['found_college']:
                row, column, found_category = add_to_row(row, column, found_category, file_name, education_content_db)
                
            if 'found_college' not in learn_order:
                count = count + 1
                learn_order['found_college'] = count
            else:
                found_category = check_learn_order(learn_order, found_category, "found_college", input_string)
                                
            column['cv_college'] = original_input_string
            column['matched_college'] = matched_college
            column['college_line'] = word
            found_category['found_college'] = True
            for val in original_input_string.split(" "):
                input_string = input_string.replace(val, '')
        
        #if not (found_college or found_year or found_degree):
        if input_string:
            unprocessed_string.append(input_string)
        #print column
        #print learn_order
        #print found_category
        #print "========================================="
            
    unprocessed = ' '.join(unprocessed_string)
    if len(unprocessed) > 6000:
        unprocessed = unprocessed[:6000]
    for found, value in found_category.iteritems():
        if value:
            column['file_name'] = file_name
            column['education_content'] = education_content_db
            row.append(column)
            break
    unprocessed = [{'file_name': file_name, 'unprocessed': unprocessed}]
    return (row, unprocessed)

def convert_to_df(data_list):
    df = pd.DataFrame(data_list)
    df_clean = df.where((pd.notnull(df)), None)
    df_clean = df.where((pd.notnull(df)), 0)
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
    diff_rows = df.groupby(list(df.columns))
    diff_df_rows = [x[0] for x in diff_rows.groups.values() if len(x) == 1]
    

def categorize_education_info(cv):
    utility = Utility()
    #education_info = utility.read_from_json(edu_json_path)
    education_error_files = list()
    forward_parse_result = list()
    reverse_parse_result = list()
    forward_unparsed = list()
    reverse_unparsed = list()
    
    try:
        education_content = str(cv["education"])
        file_name = str(cv["file_name"])
        
        word_list = education_content.split("|")
        (forward_processed, forward_unprocessed) = education_parsing(word_list, file_name, education_content)
        if not forward_processed:
            raise Exception("No data parsed from education ********************")
        
        forward_parse_result.extend(forward_processed)
        forward_unparsed.extend(forward_unprocessed)
        
    except Exception, e:
        utility.write_to_text_file(FAILED_EDUCATION_JSON_PARSE, cv["file_name"]+"','" )
    
    forward_parse = convert_to_df(forward_parse_result)
    reverse_parse = convert_to_df(reverse_parse_result)
    forward_unparsed = convert_to_df(forward_unparsed)
    reverse_unparsed = convert_to_df(reverse_unparsed)
    put_parse_data_to_db(forward_parse, reverse_parse, forward_unparsed, reverse_unparsed)
    
    #compare_diff_of_forward_reverse_parse(forward_parse, reverse_parse)

