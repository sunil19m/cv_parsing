import os
from glob import glob
from BeautifulSoup import BeautifulSoup
import sys
import re
import json
import traceback

from constant import (PDF_FILE_PATH,
                      EDUCATION_FILE_PATH,
                      NO_BOLD_CV_FILE_PATH,
                      ERROR_FILE_PATH,
                      ALL_LABELS_CV_FILE_PATH,
                      UNMATCHED_EDUCATION_BOLD)


def fetch_pdf_files(file_path):
    return glob(file_path + "*.pdf")

def convert_pdf_to_html(pdf_file):
    os.system('pdftohtml -f 1 -l 1 -q '+ pdf_file)

def clean_text_values(text_value):
    text_value = re.sub('&#160;', ' ', text_value)
    text_value = re.sub(r"\\\w+", " ", text_value)
    text_value = re.sub('[^a-zA-Z0-9-_*.@(),]', ' ', text_value)
    return text_value

def fetch_bold_header_contants(html, actual_file_name):
    result = dict()
    soup = BeautifulSoup(html)
    bold = soup.find("b")
    
    if bold:
        inside_bold_string = ''
        bold_heading = str(clean_text_values(bold.text)).strip()
        bold = bold.next
        bold = bold.next
        while(bold):
            cur_bold = BeautifulSoup(str(bold))            
            if cur_bold.find("b"):
                result[bold_heading] = str(inside_bold_string).strip()
                inside_bold_string = ''
                bold_heading = str(clean_text_values(cur_bold.text)).strip()
                bold = bold.next
                bold = bold.next
                continue
            inside_bold_string = str(inside_bold_string).strip() + " " +\
                str(clean_text_values(cur_bold.text)).strip()
            bold = bold.next
        result[bold_heading] = str(inside_bold_string).strip()
        result["file_name"] = actual_file_name
        return result
    else:
        return None

def write_json_to_text_file(file_path, json_data):
    if json_data:
        with open(file_path, 'w') as fp:
            json.dump(json_data, fp)

def extract_bold_header_section(file_path, actual_file_name):
    reload(sys)  
    sys.setdefaultencoding('latin-1')
    with open(file_path, 'r') as fp:
        html_text = fp.read()
        return fetch_bold_header_contants(html_text, actual_file_name)

def check_education_in_extracted_bold(parsed_bold, pdf_name):
    match_string = list()
    for label in parsed_bold.keys():
        match = re.match("edu.*", label, flags=re.IGNORECASE)
        if match:
            match_string.append(match.group(0))
    return match_string


def extract_education_info(parsed_bold, file_name):
    bold_headers = parsed_bold.keys()
    education_dict = dict()
    education_error_list = None
    matched_education = check_education_in_extracted_bold(parsed_bold, file_name)
    if matched_education:
        if len(matched_education) > 1:
            return None        
        education_dict['education'] = parsed_bold[matched_education[0]]
        education_dict['file_name'] = file_name
    if education_dict
        return education_dict 

def main():
    pdf_files = fetch_pdf_files(PDF_FILE_PATH)
    education_list = list()
    education_error_list = list()    
    available_bold_headers = list()
    no_bold_cv_files = list()
    error_files = list()
    for pdf in pdf_files:
        try:
            convert_pdf_to_html(pdf)
            split_pdf_extension = os.path.splitext(pdf)
            (base_path, file_name) = os.path.split(pdf)
            parsed_bold = extract_bold_header_section(split_pdf_extension[0] + "s.html", file_name)
            if not parsed_bold:
                no_bold_cv_files.append(pdf)
                continue

            # Extracting all the keys from the pdf for further analysis
            available_bold_headers.extend(parsed_bold.keys())
            
            # Education scrapping
            education = extract_education_info(parsed_bold, file_name)
            if education:
                education_list.append(education)
            else:          
                education_error_list.append(file_name)      
        except Exception, e:
            print traceback.print_exc()
            error_files.append(pdf)

    # Printing all the necessary documents
    write_json_to_text_file(EDUCATION_FILE_PATH, education_list)
    write_json_to_text_file(UNMATCHED_EDUCATION_BOLD, education_error_list)
    write_json_to_text_file(NO_BOLD_CV_FILE_PATH, no_bold_cv_files)
    write_json_to_text_file(ALL_LABELS_CV_FILE_PATH, list(set(available_bold_headers)))
    write_json_to_text_file(ERROR_FILE_PATH, error_files)

if __name__ == "__main__":
    main()
