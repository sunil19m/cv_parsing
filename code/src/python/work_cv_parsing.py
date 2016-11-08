"""
This module extract the granular information of the work related information.
It helps in extracting the institution, title, start & end year information

Once the work information section is given as input it tries to extract the work categories
using two methods.
1. Learning the order of the resume & adding blank spaces if missing
2. A plain extraction on how they appear in the pdf.

All these logics follow this belief. Once if the any of the category is found in the earlier line,
and if it encounters the same field again. Then it inserts the older line to database.
"""
import re
import traceback
from constant import (FAILED_WORK_JSON_PARSE,
                      LOGIC_CODE_CATEGORY_LEARNING_NON_BOLD,
                      LOGIC_CODE_CATEGORY_PLAIN_PARSING_BOLD,
                      LOGIC_CODE_CATEGORY_PLAIN_PARSING_NON_BOLD,
                      MULTIPLE_SEGMENT_BREAK,
                      NOISE_WORDS,
                      PRESENT_YEAR_DEFAULT_VAL,
                      WORK_META_DATA,
                      WORK_CATEGORY_MAPPING)

from college_info_trie import possible_college_search
from dao import Dao
import utility

ALL_TITLE = [re.escape(x) for x in WORK_META_DATA]
RE_TITLE = ['(^|\\s|,|:)'+x+'($|\\s|,|:)' for x in ALL_TITLE]

ALL_WORK_CATEGORY = [re.escape(x) for x in WORK_CATEGORY_MAPPING.keys()]
ALL_WORK_CATEGORY_STR = '*|'.join(ALL_WORK_CATEGORY) +'*'

def remove_noise_words(input_string):
    """
    The words like economics, finance, management creates lot of issues
    when searching against the university names. So removing these words
    """
    if input_string in NOISE_WORDS:
        return ' '
    return input_string

def category_info(input_string):
    """
    Giving a category for all the sentences available in the resume.
    For example: finance found in a string, then its given 1 etc.
    """
    category_info_match = re.search(ALL_WORK_CATEGORY_STR, input_string)
    if category_info_match:
        if category_info_match.group() in WORK_CATEGORY_MAPPING:
            return WORK_CATEGORY_MAPPING[category_info_match.group()]
    else:
        return 0


def add_to_row(row_data, column_data, found_category, file_name,\
               original_input_string, prev_matched_college, row_counts, logic_code):
    """
    Populates the appropriate fields and adds to the list of rows that must me added to the database.
    1. In the non bold logic, since the end is unknown. It restricts itself by checking if the data
       to insert has any of the title, college or category info. If not present it excludes from adding to db
    2. It propogates the previously known college names to the rows with null values
    """
    #print "&&&&&&&&&&&& Adding rows &&&&&&&&&&&&&&"
    column_data['file_name'] = file_name
    column_data['logic_code'] = logic_code
    column_data['row_info'] = original_input_string
    column_data['category_info'] = category_info(original_input_string)
    column_data['row_counts'] = row_counts

    add_row_in_db = False

    # Dont add the row if title is not available
    if logic_code == LOGIC_CODE_CATEGORY_LEARNING_NON_BOLD\
            or logic_code == LOGIC_CODE_CATEGORY_PLAIN_PARSING_NON_BOLD:
        if column_data['category_info'] or column_data['title'] or column_data['matched_college']:
            add_row_in_db = True
    else:
        add_row_in_db = True

    if add_row_in_db:
        if not column_data['matched_college']:
            column_data['matched_college'] = prev_matched_college
            if prev_matched_college.strip():
                column_data['is_college_propogated'] = 1
        row_data.append(dict(column_data))

    #print column_data
    column_data = {'start_year': None, 'end_year': None, 'title': None,\
                   'matched_college': None, 'logic_code':logic_code, 'category_info': None, 'is_college_propogated':0}
    found_category['found_college'] = False
    found_category['found_year'] = False
    found_category['found_title'] = False
    original_input_string = ""
    return row_data, column_data, found_category, original_input_string

def check_if_year(word):
    """
    If the year mentioned as current/present then its given the value 2049.
    This function also validates if the date is within 1800 & 2049.
    Takes care of parsing the year range.
    """
    y_split = word.split("-")
    space_split = list()
    for val in y_split:
        space_split.extend(val.split())

    year = list()
    for word in space_split:
        val = word.strip()
        match = re.search(r'\d+', val)
        if match:
            val = match.group(0)
            if int(val) > 1800 and int(val) < 2050:
                year.append(int(val))
    return year

def check_year_title_clg(input_string):
    """
    This function checks if the year, title, college/institution is present in the given sentence.
    It also assigns the order in which they were encountered. This forms the core for the learning agent,
    to learn the order of the categories.

    Year & title are matched using the regular expression search.
    College/Institution is found using the fuzzy logic. (Equivalance & Similarity search algorithm)
    """
    order_parse = list()
    result = {'title':None, 'start': None, 'end': None}
    year_list = list()

    year_match = re.search("\\d{4}\\s*\\d{4}|\\d{4}-\\d{4}|\\d{4}\\s*-\\s*\\d{4}|\\d{4}\\s*to\\s*\\d{4}|\\d{4}",\
            input_string)

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

    for title_pat in RE_TITLE:
        title_match = re.search(title_pat, input_string)
        if title_match:
            title_str = title_match.group()
            result['title'] = title_str
            break

    matched_college = possible_college_search(input_string)
    if matched_college:
        matched_clg_lwr = str(matched_college).lower().split()
        result['college'] = matched_college
        for word in matched_clg_lwr:
            clg_match = re.search(re.escape(word), input_string)
            if clg_match:
                break

    # If all the three categories are available
    if year_list and title_match and matched_college:
        year_pos = year_match.span()[0]
        title_pos = title_match.span()[0]
        college_pos = clg_match.span()[0]

        # Year_Match lesser
        if year_pos < title_pos:
            if year_pos < college_pos:
                order_parse.append("found_year")
                if title_pos < college_pos:
                    order_parse.append("found_title")
                    order_parse.append("found_college")
                else:
                    order_parse.append("found_college")
                    order_parse.append("found_title")
            else:
                order_parse.append("found_college")
                order_parse.append("found_year")
                order_parse.append("found_title")
        else:
            if title_pos < college_pos:
                order_parse.append("found_title")
                if year_pos < college_pos:
                    order_parse.append("found_year")
                    order_parse.append("found_college")
                else:
                    order_parse.append("found_college")
                    order_parse.append("found_year")
            else:
                order_parse.append("found_college")
                order_parse.append("found_title")
                order_parse.append("found_year")

    # If only two categories are available
    elif year_list and title_match:
        year_pos = year_match.span()[0]
        title_pos = title_match.span()[0]
        if year_pos < title_pos:
            order_parse.append("found_year")
            order_parse.append("found_title")
        else:
            order_parse.append("found_title")
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

    elif title_match and matched_college:
        title_pos = title_match.span()[0]
        college_pos = clg_match.span()[0]
        if title_pos < college_pos:
            order_parse.append("found_title")
            order_parse.append("found_college")
        else:
            order_parse.append("found_college")
            order_parse.append("found_title")

    # If only one category is available
    elif year_list:
        year_pos = year_match.span()[0]
        order_parse.append("found_year")

    elif title_match:
        title_pos = title_match.span()[0]
        order_parse.append("found_title")

    elif matched_college:
        college_pos = clg_match.span()[0]
        order_parse.append("found_college")

    #print order_parse, result
    return (order_parse, result)

def check_learn_order(learn_order, found_category, category, logic_code):
    """
    This function checks if the found categories are preserving the learn order.
    If this is violated, then null values are added appropriately.
    Example:
        If learn_order is {year:1, title:2, college:3}
        Now if the college is found and other two are not available. Then it puts null values
        to these two values.
    """
    if logic_code == LOGIC_CODE_CATEGORY_PLAIN_PARSING_BOLD\
            or logic_code == LOGIC_CODE_CATEGORY_PLAIN_PARSING_NON_BOLD:
        #print "Returning"
        return found_category
    rank = learn_order[category]
    for key, value in learn_order.iteritems():
        if value < rank:
            #print "******* Setting the following true *******"
            #print value, key
            found_category[key] = True
    return found_category

def work_parsing(word_list, file_name, logic_code):
    """
    For the given word information, it iterates through each line and tries to extract different categories.
    1. If the logical_code is Learning (1,3). Then it learns the order in which different categories are inserted.
        It applies this learning category to put null values if they dont come in order.
        This is applied only when all the category are available. Till then it does the same job as plain parsing data.
    2. Year range as present then its put 2049 value.
    3. In case of different section of work "MULTIPLE_SEGMENT_BREAK", then it starts fresh by re-learning again.
    """
    column = {'start_year': None, 'end_year': None, 'title': None,\
              'matched_college': None, 'logic_code':logic_code, 'is_college_propogated':0}
    row = list()
    found_category = {'found_college': False, 'found_year': False, 'found_title': False}

    original_input_string = ""
    learn_order = dict()
    count = 0
    row_counts = 0
    prev_matched_college = ''
    is_learn_order_stable = False
    for word in word_list:
        input_string = str(word.strip()).lower()
        input_string_initial = str(input_string)
        original_input_string = original_input_string + ''

        input_string = remove_noise_words(input_string)
        if not input_string:
            continue

        start = None
        end = None
        title = None
        input_string = re.sub("present|current|pres|curr", " "+ PRESENT_YEAR_DEFAULT_VAL, input_string)

        #print input_string

        if MULTIPLE_SEGMENT_BREAK in input_string:
            for _, value in found_category.iteritems():
                if value:
                    row, column, found_category, original_input_string = add_to_row(row, column,\
                        found_category, file_name, original_input_string, prev_matched_college, row_counts, logic_code)
                    row_counts = row_counts + 1
                    prev_matched_college = ''
                    learn_order = dict()
                    found_category = {'found_college': False, 'found_year': False, 'found_title': False}
                    break

        (order_category, year_title_clg_result) = check_year_title_clg(input_string)
        if len(order_category) == 3:
            is_learn_order_stable = True

        if not is_learn_order_stable:
            learn_order = dict()
            count = 0

        for _, val in enumerate(order_category):
            if val == "found_year":
                start = year_title_clg_result["start"]
                end = year_title_clg_result["end"]

                if found_category['found_year']:
                    row, column, found_category, original_input_string = add_to_row(row, column,\
                        found_category, file_name, original_input_string, prev_matched_college,\
                        row_counts, logic_code)
                    row_counts = row_counts + 1
                if 'found_year' not in learn_order:
                    count = count + 1
                    learn_order['found_year'] = count
                else:
                    found_category = check_learn_order(learn_order, found_category, "found_year", logic_code)
                if start:
                    column['start_year'] = start
                    input_string = input_string.replace(str(start), '')

                column['end_year'] = end
                found_category['found_year'] = True
                input_string = input_string.replace(str(end), '')

            elif val == "found_title":
                title = year_title_clg_result["title"]
                if found_category['found_title']:
                    row, column, found_category, original_input_string =\
                        add_to_row(row, column, found_category, file_name,\
                            original_input_string, prev_matched_college, row_counts, logic_code)
                    row_counts = row_counts + 1
                if 'found_title' not in learn_order:
                    count = count + 1
                    learn_order['found_title'] = count
                else:
                    found_category = check_learn_order(learn_order, found_category, "found_title", logic_code)
                column['title'] = title
                found_category['found_title'] = True
                input_string = input_string.replace(title, '')

            elif val == "found_college":
                # Check for college
                matched_college = year_title_clg_result["college"]
                prev_matched_college = matched_college
                if found_category['found_college']:
                    row, column, found_category, original_input_string =\
                        add_to_row(row, column, found_category, file_name,\
                            original_input_string, prev_matched_college, row_counts, logic_code)
                    row_counts = row_counts + 1
                if 'found_college' not in learn_order:
                    count = count + 1
                    learn_order['found_college'] = count
                else:
                    found_category = check_learn_order(learn_order, found_category, "found_college", logic_code)
                column['matched_college'] = matched_college
                found_category['found_college'] = True

        original_input_string = original_input_string + ' | ' + input_string_initial
        #print "************** FINAL ***************"
        #print column
        #print learn_order
        #print found_category
        #print original_input_string
        #print "========================================="

    for _, value in found_category.iteritems():
        if value:
            add_to_row(row, column, found_category, file_name,\
                       original_input_string, prev_matched_college, row_counts, logic_code)
            row_counts = row_counts + 1
            break
    return row


def put_parse_data_to_db(parsed_data):
    """
    Insert the parsed work information into database
    """
    dao = Dao()
    dao.insert_work_raw(parsed_data)

def categorize_work_info(data, logic_code):
    """
    Master function for parsing the different work category.
    """
    parsed_data_result = list()

    try:
        work_content = str(data["work"])
        file_name = str(data["file_name"])

        word_list = work_content.split("|")
        forward_processed = work_parsing(word_list, file_name, logic_code)
        if not forward_processed:
            raise Exception("No data parsed from work ********************")
        parsed_data_result.extend(forward_processed)
    except Exception:
        print traceback.print_exc()
        utility.write_to_text_file(FAILED_WORK_JSON_PARSE, data["file_name"]+"','")

    parsed_data = utility.convert_to_df(parsed_data_result)
    put_parse_data_to_db(parsed_data)


def update_possible_error_rows(learning_logic_code, plain_logic_code):
    """
    Once both the logic are extracted. Learning agent logic & plain parsing logic.
    Both are compared if there is a mismatch in the values and given manual_check column
    is marked if there is a mismatch.
    """
    dao = Dao()
    dao.update_manual_check_work(learning_logic_code, plain_logic_code)
