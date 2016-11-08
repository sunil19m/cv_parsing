"""
    The parser script is used to parse the professors resume

    This module parses the work related information using bold logic.
    It first converts the pdf to an html file, then grabs all the bold headers as each section.
    For example: The resume will have Education, Positions, Achievements. Each seperate section is collected
        and are processed for more accurate fields like university, degree related information.
"""
import os
import re
import sys
import traceback
from constant import (CODEC_FAILURE,
                      ERROR_FILE_PATH,
                      HISTORY_LABELS,
                      LOGIC_CODE_CATEGORY_LEARNING_BOLD,
                      LOGIC_CODE_CATEGORY_PLAIN_PARSING_BOLD,
                      MULTIPLE_SEGMENT_BREAK,
                      NO_BOLD_CV_FILE_PATH,
                      PDF_FILE_PATH,
                      WORK_FILE_PATH,
                      WORK_LABELS,
                      UNMATCHED_WORK_BOLD)

from work_cv_parsing import (categorize_work_info,
                             update_possible_error_rows)
import utility

ALL_WORK_LABELS = [re.escape(x) for x in WORK_LABELS]

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

def check_work_in_extracted_bold(parsed_bold):
    """
    This function extracts only the work related labels such as employment, positions etc.
    These labels are the bold labels extracted from the html files.
    This appends current, previous etc as prefix and looks for that labels as well.
    If multiple work related are available, all are captured

    returns the [' Positions ', ' APPOINTMENTS']
    """
    match_string = list()
    for label in parsed_bold.keys():
        for work_label in ALL_WORK_LABELS:
            for prefix_label in HISTORY_LABELS:
                pattern = re.compile(prefix_label + '\\s'+ work_label+'*')
                if not prefix_label:
                    pattern = re.compile(work_label+'*', re.I)
                match = re.search(pattern, label)
                if match:
                    match_string.append(label)
                    break
    return match_string


def extract_work_info(parsed_bold, file_name):
    """
    Once the work related labels are known, all the complete section is extracted.
    The extracted is put under the field work.
    Multiple sections are appended into one by multiple segment break.
    """
    work_dict = dict()
    matched_work = check_work_in_extracted_bold(parsed_bold)
    if matched_work:
        for match in matched_work:
            work_str = work_dict.get('work', MULTIPLE_SEGMENT_BREAK)
            work_dict['work'] = work_str + parsed_bold[match].encode(sys.stdout.encoding, errors='replace')\
                + MULTIPLE_SEGMENT_BREAK
            work_dict['file_name'] = file_name
    if work_dict:
        return work_dict

def main():
    """
    1. Fetches the pdf CV's from the given location
    2. Makes into chuck of 100pdfs for processing.
    3. Extracts each pdfs and capture the bold label section related to work
    4. Gives this information for further granular extraction of different categories
        a. Learning the order of these categories and filling blank if not available
        b. Plain extraction of the categories
    5. If no bold labels found in the pdfs, then they are put to the unbold exception list
    6. Many exception lists like no data, unbold pdfs, error due to codecs are maintained
    """
    no_bold_cv_files = list()
    work_error_list = list()
    error_files = list()

    pdf_files = utility.fetch_pdf_files(PDF_FILE_PATH)
    inital_count = 0
    final_count = (len(pdf_files) + 10)
    while inital_count <= final_count:
        print "Starting chuck " + str(inital_count) + " : " + str(inital_count + 100)
        work_list = list()

        for pdf in pdf_files[inital_count:inital_count+100]:
            print pdf
            try:
                utility.convert_pdf_to_html(pdf)
                split_pdf_extension = os.path.splitext(pdf)
                (_, file_name) = os.path.split(pdf)

                # The converted pdf to html file has 's.html' at the end of the file.
                parsed_bold = extract_bold_header_section(split_pdf_extension[0] + "s.html", file_name)

                if not parsed_bold:
                    no_bold_cv_files.append(pdf)
                    continue

                work = extract_work_info(parsed_bold, file_name)
                if work:
                    work_list.append(work)
                    categorize_work_info(work, LOGIC_CODE_CATEGORY_LEARNING_BOLD)
                    categorize_work_info(work, LOGIC_CODE_CATEGORY_PLAIN_PARSING_BOLD)
                else:
                    work_error_list.append(file_name)
            except Exception:
                print traceback.print_exc()
                error_files.append(pdf)


        # Inserting the work information in chuncks
        work_file_path = os.path.join(WORK_FILE_PATH, 'work_cv_'+\
            str(inital_count) + '_' + str(inital_count + 100)+'.txt')
        if work_list:
            utility.write_json_to_text_file(work_file_path, work_list)
        inital_count = inital_count + 101

    utility.write_json_to_text_file(UNMATCHED_WORK_BOLD, work_error_list)
    utility.write_json_to_text_file(NO_BOLD_CV_FILE_PATH, no_bold_cv_files)
    utility.write_json_to_text_file(ERROR_FILE_PATH, error_files)
    update_possible_error_rows(LOGIC_CODE_CATEGORY_LEARNING_BOLD, LOGIC_CODE_CATEGORY_PLAIN_PARSING_BOLD)


if __name__ == "__main__":
    main()
