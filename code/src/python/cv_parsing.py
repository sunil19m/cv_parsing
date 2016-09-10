import os
from glob import glob
from BeautifulSoup import BeautifulSoup
import sys
import re
import json

from constant import (PDF_FILE_PATH,
                      OUTPUT_FILE_PATH,
                      NO_BOLD_CV_FILE_PATH,
                      ERROR_FILE_PATH)


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
    with open(file_path, 'w') as fp:
        json.dump(json_data, fp)

def extract_bold_header_section(file_path, actual_file_name):
    reload(sys)  
    sys.setdefaultencoding('latin-1')
    with open(file_path, 'r') as fp:
        html_text = fp.read()
        return fetch_bold_header_contants(html_text, actual_file_name)
        
def main():
    pdf_files = fetch_pdf_files(PDF_FILE_PATH)
    final_result = list()
    no_bold_cv_files = list()
    error_files = list()

    for pdf in pdf_files:
        try:
            convert_pdf_to_html(pdf)
            split_pdf_extension = os.path.splitext(pdf)
            (base_path, file_name) = os.path.split(pdf)
            result = extract_bold_header_section(split_pdf_extension[0] + "s.html", file_name)
            if result:
                final_result.append(result)
            else:
                no_bold_cv_files.append(file_name)
        except:
            error_files.append(pdf)
    write_json_to_text_file(OUTPUT_FILE_PATH, final_result)
    write_json_to_text_file(NO_BOLD_CV_FILE_PATH, no_bold_cv_files)
    write_json_to_text_file(ERROR_FILE_PATH, error_files)



if __name__ == "__main__":
    main()
