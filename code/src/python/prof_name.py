"""
    The parser script is used to parse the professors resume

    This module parses the prof_name related information using the below logic.
    It first converts the pdf to a text file using pdftotxt unix command.
    - This uses two logics
        Intelligent search: Checks if its not in the english dictionary and adds first 3 words
        Simple search: Just adds first 3 words available from the first line
    - First tries to find the name in the first line. If nothing is found then looks for first 4 lines.
        Intelligent search line = 1 or 4 based on this logic. Similarly simple search aswell.
"""
import os
import re
import sys
import traceback

import enchant
from constant import (CODEC_FAILURE,
                      ERROR_FILE_PATH,
                      PDF_FILE_PATH,
                      WORK_FILE_PATH,
                      WORK_LABELS,
                      UNMATCHED_WORK)

from dao import Dao
import utility


ALL_WORK_LABELS = [re.escape(x) for x in WORK_LABELS]
def clean_text_values(text_value):
    """
    The pdf when converted will have many special & hexadecimal characters.
    The function helps in removing those characters
    """
    text_value = text_value.replace("\xc2\xa0", " ")
    text_value = text_value.replace("\xc2", " ")
    text_value = text_value.replace("\xa0", " ")
    text_value = re.sub('[^a-zA-Z\\s+\n]', '', text_value)
    return text_value

def add_prof_names(name, prev_txt, count, intel_txt_recognization=True):
    """
    This function adds word to the list if its not in the english dictionary (Intelligent search)
    Else if its simple search it adds the first 3 words available.
    """
    txt = prev_txt
    en_dictionary = enchant.Dict("en_US")
    if intel_txt_recognization:
        if len(name) == 1 or not en_dictionary.check(name):
            count = count + 1
            txt = txt + ' ' + name.encode("latin-1").decode().strip()
    else:
        count = count + 1
        txt = txt + ' ' + name.encode("latin-1").decode().strip()
    return (txt, count)

def parse_prof_name(pdf_text, intel_txt_recognization):
    """
    This function adds word to the list if its not in the english dictionary (Intelligent search)
    Else if its simple search it adds the first 3 words available.
    """
    txt = ''
    count = 0
    while True:
        match = re.match("(^[\\s+\\w]\\w*)", pdf_text)
        if match:
            name = match.group(0)
            name = name.strip()
            (_, end) = match.span()
            pdf_text = pdf_text[end + 1:]
            if not name:
                continue
            txt, count = add_prof_names(name, txt, count, intel_txt_recognization)
            if count >= 3:
                break
        else:
            break
    return txt

def extract_name_part(pdf_text):
    """
    From the pdf tries to parse the name from the first line if not information
    is parsed then selects the top 4 lines for parsing
    This uses two logics
        Intelligent search: Checks if its not in the english dictionary and adds first 3 words
        Simple search: Just adds first 3 words available from the first line
    """
    # Uses the first line only for searching the name
    intelligent_txt_line = 1
    simple_txt_line = 1
    pdf_text = clean_text_values(pdf_text)
    pdf_text_new = pdf_text.split("\n")[0]
    copy_pdf_text = str(pdf_text_new)
    intelligent_txt = parse_prof_name(pdf_text_new, intel_txt_recognization=True)
    simple_txt = parse_prof_name(pdf_text_new, intel_txt_recognization=False)
    if simple_txt and intelligent_txt:
        return (intelligent_txt.strip(), simple_txt.strip(), intelligent_txt_line, simple_txt_line)

    # Uses the first 4 lines from pdf
    pdf_text_new = ' '.join(pdf_text.split("\n")[:4])
    copy_pdf_text = str(pdf_text_new)
    if not intelligent_txt:
        intelligent_txt = parse_prof_name(copy_pdf_text, intel_txt_recognization=True)
        intelligent_txt_line = 4
    if not simple_txt:
        simple_txt = parse_prof_name(copy_pdf_text, intel_txt_recognization=False)
        simple_txt_line = 4
    return (intelligent_txt.strip(), simple_txt.strip(), intelligent_txt_line, simple_txt_line)

def extract_text_from_pdf(pdf_text, file_name):
    """
    Returns the extracted prof_name information as a dictionary
    """
    prof_name_data = dict()
    pdf_text = pdf_text.lower()

    (intelligent_txt, simple_txt, intelligent_txt_line, simple_txt_line) = extract_name_part(pdf_text)
    prof_name_data['file_name'] = file_name
    prof_name_data['prof_name_intelligent'] = intelligent_txt
    prof_name_data['prof_name_simple'] = simple_txt
    prof_name_data['prof_name_intelligent_line'] = intelligent_txt_line
    prof_name_data['prof_name_simple_line'] = simple_txt_line
    return prof_name_data

def extract_prof_name_section(file_path, actual_file_name):
    """
    Opens the converted pdf to text file & tries to extract the prof_name information with different unicodes.
    """
    reload(sys)
    sys.setdefaultencoding('latin-1')
    with open(file_path, 'r') as fp:
        try:
            pdf_text = str(fp.read())
            return extract_text_from_pdf(pdf_text[:1000], actual_file_name)
        except Exception:
            print traceback.print_exc()
            utility.write_to_text_file(CODEC_FAILURE, file_path+"','")

def put_parse_data_to_db(parsed_data):
    """
    Insert the parsed prof_name information into database
    """
    dao = Dao()
    dao.insert_prof_name_raw(parsed_data)

def main():
    """
    1. Fetches the pdf CV's from the given location
    2. Makes into chuck of 100 pdfs for processing.
    3. Converts the pdf to text file using the unix commad pdftotext
    4. Extracts the prof name information from the text file.
    5. This uses two logics
        Intelligent search: Checks if its not in the english dictionary and adds first 3 words
        Simple search: Just adds first 3 words available from the first line
    6. First tries to find the name in the first line. If nothing is found then looks for first 4 lines.
        Intelligent search line = 1 or 4 based on this logic. Similarly simple search aswell.
    7. Maintains an exception list for catching all the different exception
    8. Many exception lists like no data, unmatched prof_name information, error due to codecs are maintained
    """
    prof_name_error_list = list()
    error_files = list()

    pdf_files = utility.fetch_pdf_files(PDF_FILE_PATH)
    inital_count = 0
    final_count = (len(pdf_files) + 10)
    prof_name_list = list()
    while inital_count <= final_count:
        print "Starting chuck " + str(inital_count) + " : " + str(inital_count + 100)
        for pdf in pdf_files[inital_count:inital_count+100]:
            print pdf
            try:
                utility.convert_pdf_to_text(pdf)
                split_pdf_extension = os.path.splitext(pdf)
                (_, file_name) = os.path.split(pdf)

                # prof_name scrapping
                prof_name = extract_prof_name_section(split_pdf_extension[0] + ".txt", file_name)
                if prof_name:
                    prof_name_list.append(prof_name)
                else:
                    prof_name_error_list.append(file_name)
            except Exception:
                print traceback.print_exc()
                error_files.append(pdf)

        # Inserting the prof_name information in chuncks
        prof_name_file_path = os.path.join(WORK_FILE_PATH,\
            'prof_name_cv_' + str(inital_count) + '_' + str(inital_count + 100) + '.txt')
        if prof_name_list:
            utility.write_json_to_text_file(prof_name_file_path, prof_name_list)
        inital_count = inital_count + 101

    parsed_data = utility.convert_to_df(prof_name_list)
    put_parse_data_to_db(parsed_data)
    utility.write_json_to_text_file(UNMATCHED_WORK, prof_name_error_list)
    utility.write_json_to_text_file(ERROR_FILE_PATH, error_files)

if __name__ == "__main__":
    main()
