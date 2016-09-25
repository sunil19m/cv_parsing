import os
from glob import glob
from BeautifulSoup import BeautifulSoup
from BeautifulSoup import NavigableString
import sys
import re
import json
import traceback

from education import categorize_education_info

from constant import (PDF_FILE_PATH,
                      EDUCATION_FILE_PATH,
                      NO_BOLD_CV_FILE_PATH,
                      ERROR_FILE_PATH,
                      ALL_LABELS_CV_FILE_PATH,
                      UNMATCHED_EDUCATION_BOLD)

from utility import Utility

def fetch_bold_header_contants(html, actual_file_name):
    reload(sys)  
    sys.setdefaultencoding('cp1252')
    
    utility = Utility()
    result = dict()
    soup = BeautifulSoup(html)
    bold = soup.find("b")
    if bold:
        old_bold_text = bold.text
        inside_bold_string = ''
        bold_heading = str(utility.clean_text_values(old_bold_text)).strip()
        try:
            while(old_bold_text == bold.text):
                bold = bold.next
        except Exception:
            pass
        while(bold):
            cur_bold = BeautifulSoup(str(bold))
            old_bold_text = cur_bold.text   
            if cur_bold.find("b"):
                old_bold_text = bold.text
                result[bold_heading] = str(utility.clean_text_values(inside_bold_string)).strip()
                inside_bold_string = ''
                bold_heading = str(utility.clean_text_values(cur_bold.text)).strip()
                
            else:
                inside_bold_string = str(utility.clean_text_values(inside_bold_string)).strip() + "|" +\
                str(utility.clean_text_values(cur_bold.text)).strip()
            if bold:
                bold = bold.next
                while (old_bold_text == bold):
                    bold = bold.next
            else:
                break
        result[bold_heading] = str(utility.clean_text_values(inside_bold_string)).strip()
        result["file_name"] = actual_file_name
        return result
    else:
        return None

def extract_bold_header_section(file_path, actual_file_name):
    reload(sys)  
    sys.setdefaultencoding('cp1252')
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
        education_dict['education'] = parsed_bold[matched_education[0]].encode(sys.stdout.encoding, errors='replace')
        education_dict['file_name'] = file_name
    if education_dict:
        return education_dict 

def main():
    reload(sys)  
    sys.setdefaultencoding('cp1252')
    utility = Utility()
    education_error_list = list()    
    no_bold_cv_files = list()
    error_files = list()
    #available_bold_headers = list()

    pdf_files = utility.fetch_pdf_files(PDF_FILE_PATH)
    inital_count = 0
    final_count = (len(pdf_files) + 10)
    window = 100
    while(inital_count <= final_count):        
        print "Starting chuck " + str(inital_count) + " : " + str(inital_count + 100) 
        education_list = list()       
        
        for pdf in pdf_files[inital_count:inital_count+100]:
            print pdf
            try:
                utility.convert_pdf_to_html(pdf)
                split_pdf_extension = os.path.splitext(pdf)
                (base_path, file_name) = os.path.split(pdf)
                parsed_bold = extract_bold_header_section(split_pdf_extension[0] + "s.html", file_name)
                if not parsed_bold:
                    no_bold_cv_files.append(pdf)
                    continue

                # Extracting all the keys from the pdf for further analysis
                #available_bold_headers.extend(parsed_bold.keys())
                
                # Education scrapping
                education = extract_education_info(parsed_bold, file_name)
                if education:
                    education_list.append(education)
                    categorize_education_info(education)
                else:
                    education_error_list.append(file_name)      
            except Exception, e:
                print traceback.print_exc()
                error_files.append(pdf)


        # Inserting the education information in chuncks
        education_file_path = os.path.join(EDUCATION_FILE_PATH, 'education_cv_'
            +str(inital_count)+'_' + str(inital_count + 100)+'.txt')
        if education_list:
            utility.write_json_to_text_file(education_file_path, education_list)
            #categorize_education_info(education_file_path)
        inital_count = inital_count + 101
        
        
    utility.write_json_to_text_file(UNMATCHED_EDUCATION_BOLD, education_error_list)
    utility.write_json_to_text_file(NO_BOLD_CV_FILE_PATH, no_bold_cv_files)
    utility.write_json_to_text_file(ERROR_FILE_PATH, error_files)
    #utility.write_json_to_text_file(ALL_LABELS_CV_FILE_PATH, list(set(available_bold_headers)))    
    #remove_html_png_jpg_create_files(PDF_FILE_PATH)


if __name__ == "__main__":
    main()
