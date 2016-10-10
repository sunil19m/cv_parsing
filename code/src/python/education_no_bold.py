

import json
from college_info_trie import possible_college_search
from dao import Dao
import pandas as pd

from constant import (FAILED_EDUCATION_JSON_PARSE,
                      NOISE_WORDS,
                      DEGREE_META_DATA,
                      MORE_DEGREES)
from utility import Utility

import traceback
import re

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

def add_to_row(row_data, column_data, found_category, file_name, education_content, row_count_pdf):
    #print "&&&&&&&&&&&&"
    #print column_data
    column_data['file_name'] = file_name
    column_data['education_content'] = education_content
    column_data['logic_code'] = 2

    # Dont add the row if degree is not available
    if (column_data['degree']):
        row_data.append(dict(column_data))
        row_count_pdf = row_count_pdf + 1

    column_data = {'start_year': None, 'end_year': None, 'degree': None,\
                   'cv_college': None, 'matched_college': None, 'logic_code':2}
    found_category['found_college'] = False
    found_category['found_year'] = False  
    found_category['found_degree'] = False
    return row_data, column_data, found_category, row_count_pdf


ALL_DEGREES = [re.escape(x) for x in DEGREE_META_DATA]
ALL_DEGREES.extend([re.escape(x) for x in MORE_DEGREES])
RE_DREGREE = ['(^|\s|,|:)'+x+'($|\s|,|:)' for x in ALL_DEGREES]

def check_if_year(word):

    y_split = word.split("-")
    space_split = list()
    for val in y_split:
        space_split.extend(val.split())
    
    year = list()
    for word in space_split:
        val = word.strip()
        match = re.search(r'\d+',val)
        if match:
            val = match.group(0)
            if int(val) > 1800 and int(val) < 2050:
                year.append(int(val))
    return year

def check_year_degree_clg(input_string):
    found_year = False
    found_degree = False
    order_parse = list()
    result = {'degree':None, 'start': None, 'end': None}
    word_list = input_string.split(" ")
    word_list_comma = list()
    year_list = list()

    year_match = re.search("\d{4}\s+\d{4}|\d{4}-\d{4}|\d{4}\s+-\s+\d{4}|\d{4}", input_string)
    if year_match:
        year_str = year_match.group()
        year_list = check_if_year(year_str)
    if year_list:
        if len(year_list) > 1:
            result['end'] = year_list[1]
            result['start'] = year_list[0]
        else:
            result['end'] = year_list[0]
            result['start'] = None

    for degree_pat in RE_DREGREE:
        degree_match = re.search(degree_pat, input_string)
        if degree_match:
            degree_str = degree_match.group()
            result['degree'] = degree_str
            break

    matched_college = possible_college_search(input_string)
    if matched_college:
        matched_clg_lwr = str(matched_college).lower().split()
        result['college'] = matched_college
        for word in matched_clg_lwr:
            clg_match = re.search(re.escape(word), input_string)
            if clg_match:
                break

    if year_list and degree_match and matched_college:
        year_pos = year_match.span()[0]
        degree_pos = degree_match.span()[0]
        college_pos = clg_match.span()[0]

        # Year_Match lesser
        if year_pos < degree_pos:
            if year_pos < college_pos:
                order_parse.append("found_year")
                if degree_pos < college_pos:
                    order_parse.append("found_degree")
                    order_parse.append("found_college")
                else:
                    order_parse.append("found_college")
                    order_parse.append("found_degree")
            else:
                order_parse.append("found_college")
                order_parse.append("found_year")
                order_parse.append("found_degree")
        else:
            if degree_pos < college_pos:
                order_parse.append("found_degree")
                if year_pos < college_pos:
                    order_parse.append("found_year")
                    order_parse.append("found_college")
                else:
                    order_parse.append("found_college")
                    order_parse.append("found_year")
            else:
                order_parse.append("found_college")
                order_parse.append("found_degree")
                order_parse.append("found_year")

    elif year_list and degree_match:
        year_pos = year_match.span()[0]
        degree_pos = degree_match.span()[0]
        if year_pos < degree_pos:
            order_parse.append("found_year")
            order_parse.append("found_degree")
        else:
            order_parse.append("found_degree")
            order_parse.append("found_year")

    elif year_list and matched_college:
        year_pos = year_match.span()[0]
        college_pos = clg_match.span()[0]
        if year_pos < college_pos:
            order_parse.append("found_year")
            order_parse.append("found_college")
        else:
            order_parse.append("found_college")
            order_parse.append("found_year")

    elif degree_match and matched_college:
        degree_pos = degree_match.span()[0]
        college_pos = clg_match.span()[0]
        if degree_pos < college_pos:
            order_parse.append("found_degree")
            order_parse.append("found_college")
        else:
            order_parse.append("found_college")
            order_parse.append("found_degree")

    elif year_list:
        year_pos = year_match.span()[0]
        order_parse.append("found_year")

    elif degree_match:
        degree_pos = degree_match.span()[0]
        order_parse.append("found_degree")

    elif matched_college:
        college_pos = clg_match.span()[0]
        order_parse.append("found_college")

    
    #print order_parse, result
    return (order_parse, result)

def check_learn_order(learn_order, found_category, category, input_string):
    #print learn_order, found_category, category, input_string
    rank = learn_order[category]
    for key, value in learn_order.iteritems():
        if value < rank:
            #print "Setting the following true *******"
            #print value, key
            found_category[key] = True
    return found_category

def education_parsing(word_list, file_name, education_content):
    education_content_db = education_content[:7000]

    column = {'start_year': None, 'end_year': None, 'degree': None,\
              'cv_college': None, 'matched_college': None, 'logic_code':2}
    row = list()
    found_category = {'found_college': False, 'found_year': False, 'found_degree': False}

    unprocessed_string = list()
    
    learn_order = dict()
    count = 0
    num_rows = 0
    found_min_rows = False
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
        (order_category, year_degree_clg_result) = check_year_degree_clg(input_string)
        
        for idx, val in enumerate(order_category):
            if val == "found_year":
                start = year_degree_clg_result["start"]
                end = year_degree_clg_result["end"]

                if found_category['found_year']:  
                    row, column, found_category, num_rows = add_to_row(row, column, found_category, file_name, education_content_db, num_rows)
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
                degree = year_degree_clg_result["degree"]
                if found_category['found_degree']:
                    row, column, found_category, num_rows = add_to_row(row, column, found_category, file_name, education_content_db, num_rows)
                if 'found_degree' not in learn_order:
                    count = count + 1
                    learn_order['found_degree'] = count
                else:
                    found_category = check_learn_order(learn_order, found_category, "found_degree", input_string)
                column['degree'] = degree                
                found_category['found_degree'] = True
                input_string = input_string.replace(degree, '')

            elif val == "found_college":
                # Check for college
                matched_college = year_degree_clg_result["college"]
                if found_category['found_college']:
                    row, column, found_category, num_rows = add_to_row(row, column, found_category, file_name, education_content_db, num_rows)
                if 'found_college' not in learn_order:
                    count = count + 1
                    learn_order['found_college'] = count
                else:
                    found_category = check_learn_order(learn_order, found_category, "found_college", input_string)
                                    
                column['cv_college'] = original_input_string
                column['matched_college'] = matched_college
                found_category['found_college'] = True
        
        #print column
        #print learn_order
        #print found_category
        #print "========================================="

        if num_rows > 4:
            found_min_rows = True
            break
        #print num_rows
            
    if not found_min_rows:
        for found, value in found_category.iteritems():
            if value:
                add_to_row(row, column, found_category, file_name, education_content_db, num_rows)
                break
    return row

def convert_to_df(data_list):
    df = pd.DataFrame(data_list)
    df_clean = df.where((pd.notnull(df)), None)
    df_clean = df.where((pd.notnull(df)), 0)
    return df_clean

def put_parse_data_to_db(forward_parse):
    dao = Dao()
    dao.insert_education_raw(forward_parse)
    
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
    
    try:
        education_content = str(cv["education"])
        file_name = str(cv["file_name"])
        
        word_list = education_content.split("|")
        forward_processed = education_parsing(word_list, file_name, education_content)
        if not forward_processed:
            raise Exception("No data parsed from education ********************")
        
        forward_parse_result.extend(forward_processed)
        
        
    except Exception, e:
        print traceback.print_exc()
        utility.write_to_text_file(FAILED_EDUCATION_JSON_PARSE, cv["file_name"]+"','" )
    
    forward_parse = convert_to_df(forward_parse_result)
    put_parse_data_to_db(forward_parse)
    
    #compare_diff_of_forward_reverse_parse(forward_parse, reverse_parse)
