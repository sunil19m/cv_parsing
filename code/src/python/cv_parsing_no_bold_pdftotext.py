import os
from glob import glob
from BeautifulSoup import BeautifulSoup
from BeautifulSoup import NavigableString
import sys
import re
import json
import traceback

from education_no_bold import categorize_education_info

from constant import (PDF_FILE_PATH,
                      EDUCATION_FILE_PATH,
                      NO_BOLD_CV_FILE_PATH,
                      ERROR_FILE_PATH,
                      ALL_LABELS_CV_FILE_PATH,
                      UNMATCHED_EDUCATION_BOLD,
                      CODEC_FAILURE)

from utility import Utility

def clean_text_values(text_value):
    text_value = text_value.replace("\xc2\xa0", " ")
    text_value = text_value.replace("\xc2", " ")
    text_value = text_value.replace("\xa0", " ")
    #text_value = re.sub("!~@#$%^&*();:<>?", " ", text_value)
    text_value = re.sub('^[\w\s,|.\d]', ' ', text_value)
    text_value = re.sub("[!~@#$%^&*();:<>?]", " ", text_value)
    return text_value

def extract_education_part(pdf_text):
    utility = Utility()
    pattern = re.compile(r'education*')
    match = pattern.search(pdf_text)
    if not match:
        return None
    (start, end) = match.span()
    txt = pdf_text[start:start + 1000]
    txt = re.sub('\n', '|', txt)
    txt = str(clean_text_values(txt).encode("latin-1").decode()).strip()
    return txt

#paths = ["/media/sunil/Others/cv_parsing/data/CV/727.pdf", "/media/sunil/Others/cv_parsing/data/CV/74.pdf"]

def extract_text_from_pdf(pdf_text, file_name):
    edu_data = dict()
    pdf_text = pdf_text.lower()

    education_text = extract_education_part(pdf_text)
    if education_text:
        edu_data['file_name'] = file_name
        edu_data['education'] = education_text
    return edu_data


def extract_education_section(file_path, actual_file_name):
    reload(sys)  
    sys.setdefaultencoding('latin-1')
    with open(file_path, 'r') as fp:
        try:
            pdf_text = str(fp.read())
            return extract_text_from_pdf(pdf_text, actual_file_name)
        except Exception, e1:
            utility = Utility()
            print traceback.print_exc()
            utility.write_to_text_file(CODEC_FAILURE, file_path+"','" )
                      
def main():
    utility = Utility()
    education_error_list = list()    
    error_files = list()
    
    pdf_files = utility.fetch_pdf_files(PDF_FILE_PATH)
    inital_count = 0
    final_count = (len(pdf_files) + 10)
    while(inital_count <= final_count):        
        print "Starting chuck " + str(inital_count) + " : " + str(inital_count + 100) 
        education_list = list()       
        
        for pdf in pdf_files[inital_count:inital_count+100]:
            print pdf
            try:
                utility.convert_pdf_to_text(pdf)
                split_pdf_extension = os.path.splitext(pdf)
                (base_path, file_name) = os.path.split(pdf)
                
                # Education scrapping
                education = extract_education_section(split_pdf_extension[0] + ".txt", file_name)
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
        inital_count = inital_count + 101
    
    utility.write_json_to_text_file(UNMATCHED_EDUCATION_BOLD, education_error_list)
    utility.write_json_to_text_file(ERROR_FILE_PATH, error_files)


if __name__ == "__main__":
    main()
