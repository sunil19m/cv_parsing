"""
    The parser script is used to parse the professors resume

    This module parses the education related information using bold logic.
    It first converts the pdf to an html file, then grabs all the bold headers as each section.
    For example: The resume will have Education, Positions, Achievements. Each seperate section is collected
        and are processed for more accurate fields like university, degree related information.
"""
import os
import re
import sys
import traceback
from constant import (ALL_LABELS_CV_FILE_PATH,
                      CODEC_FAILURE,
                      ERROR_FILE_PATH,
                      EDUCATION_FILE_PATH,
                      LOGIC_CODE_CATEGORY_LEARNING_BOLD,
                      LOGIC_CODE_CATEGORY_PLAIN_PARSING_BOLD,
                      NO_BOLD_CV_FILE_PATH,
                      PDF_FILE_PATH,
                      UNMATCHED_EDUCATION_BOLD)

from education_cv_parsing import (categorize_education_info,
                                  update_possible_error_rows)
import utility

def extract_bold_header_section(file_path, actual_file_name):
    """
    Opens the html file path & tries to extract the bold sections with different unicodes.
    """
    reload(sys)
    sys.setdefaultencoding('latin-1')
    with open(file_path, 'r') as fp:
        try:
            html_text = str(fp.read())
            return utility.fetch_bold_header_contents(html_text, actual_file_name)
        except Exception:
            print traceback.print_exc()
            utility.write_to_text_file(CODEC_FAILURE, file_path+"','")

def extract_education_bold(parsed_bold):
    """
    This function extracts only the education related labels such as employment etc.
    These labels are the bold labels extracted from the html files.
    returns the [' Education ']
    """
    match_string = list()
    for label in parsed_bold.keys():
        match = re.match("edu.*", label, flags=re.IGNORECASE)
        if match:
            match_string.append(match.group(0))
    return match_string

def extract_education_info(parsed_bold, file_name):
    """
    Once the education related labels are known, the complete section is extracted.
    The extracted is put under the field education.
    """
    education_dict = dict()
    matched_education = extract_education_bold(parsed_bold)
    if matched_education:
        if len(matched_education) > 1:
            return None
        education_dict['education'] = parsed_bold[matched_education[0]].encode(sys.stdout.encoding, errors='replace')
        education_dict['file_name'] = file_name
    if education_dict:
        return education_dict

def normalize_available_labels(available_bold_headers):
    """
    This function is to omit the bold labels with characters greater than 150.
    """
    normalized_labels = list()
    try:
        for label in available_bold_headers:
            if len(label) > 150:
                continue
            normalized_labels.append(label)
    except Exception:
        pass
    return normalized_labels

def main():
    """
    1. Fetches the pdf CV's from the given location
    2. Makes into chuck of 100 pdfs for processing.
    3. Extracts each pdfs and capture the bold label section related to education
    4. Gives this information for further granular extraction of different categories
        a. Learning the order of these categories and filling blank if not available
        b. Plain extraction of the categories
    5. If no bold labels found in the pdfs, then they are put to the unbold exception list
    6. Many exception lists like no data, unbold pdfs, error due to codecs are maintained
    """
    education_error_list = list()
    no_bold_cv_files = list()
    error_files = list()
    available_bold_headers = list()

    pdf_files = utility.fetch_pdf_files(PDF_FILE_PATH)
    inital_count = 0
    final_count = (len(pdf_files) + 10)
    while inital_count <= final_count:
        print "Starting chuck " + str(inital_count) + " : " + str(inital_count + 100)
        education_list = list()

        for pdf in pdf_files[inital_count:inital_count+100]:
            print pdf
            try:
                utility.convert_pdf_to_html(pdf)
                split_pdf_extension = os.path.splitext(pdf)
                (_, file_name) = os.path.split(pdf)
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
                    categorize_education_info(education, LOGIC_CODE_CATEGORY_LEARNING_BOLD)
                    categorize_education_info(education, LOGIC_CODE_CATEGORY_PLAIN_PARSING_BOLD)
                else:
                    education_error_list.append(file_name)
            except Exception:
                print traceback.print_exc()
                error_files.append(pdf)


        # Inserting the education information in chuncks
        education_file_path = os.path.join(EDUCATION_FILE_PATH, 'education_cv_'\
            + str(inital_count) + '_' + str(inital_count + 100) + '.txt')
        if education_list:
            utility.write_json_to_text_file(education_file_path, education_list)
            #categorize_education_info(education_file_path)
        inital_count = inital_count + 101

    normalized_labels = normalize_available_labels(available_bold_headers)
    utility.write_json_to_text_file(UNMATCHED_EDUCATION_BOLD, education_error_list)
    utility.write_json_to_text_file(NO_BOLD_CV_FILE_PATH, no_bold_cv_files)
    utility.write_json_to_text_file(ERROR_FILE_PATH, error_files)
    utility.write_json_to_text_file(ALL_LABELS_CV_FILE_PATH, list(set(normalized_labels)))
    update_possible_error_rows(LOGIC_CODE_CATEGORY_LEARNING_BOLD,
                               LOGIC_CODE_CATEGORY_PLAIN_PARSING_BOLD)


if __name__ == "__main__":
    main()
