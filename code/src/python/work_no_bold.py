"""
    The parser script is used to parse the professors resume

    This module parses the work related information using the below logic.
    It first converts the pdf to a text file using pdftotxt unix command.
    For example: The resume will have Education, Positions, Achievements. Each work related section is collected
        and are processed for more accurate fields like university, degree related information.
"""
import os
import re
import sys
import traceback
from constant import (CODEC_FAILURE,
                      ERROR_FILE_PATH,
                      HISTORY_LABELS,
                      LOGIC_CODE_CATEGORY_LEARNING_NON_BOLD,
                      LOGIC_CODE_CATEGORY_PLAIN_PARSING_NON_BOLD,
                      MULTIPLE_SEGMENT_BREAK,
                      NO_BOLD_CV_FILE_PATH,
                      PDF_FILE_PATH,
                      WORK_FILE_PATH,
                      WORK_LABELS,
                      UNMATCHED_WORK)

from work_cv_parsing import (categorize_work_info,
                             update_possible_error_rows)
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
    text_value = re.sub(r'^[\w\s,|.\d]', ' ', text_value)
    text_value = re.sub("[!~@#$%^&*();:<>?]", " ", text_value)
    return text_value

def extract_work_part(pdf_text):
    """
    1. All work labels have string such as Positions, work, appointment.
    2. History labels are the prefixes to all work labels, previous, current, past etc.
    3. Since we dont know where this part of the section ends it takes the first 1000 characters
    from where the it found the work matching pattern.
    4. It makes sure that once the pattern is selected in the previous label is again not checked
    for pattern matching. To avoid duplication.
    5. Returns the string of work related information from the resume.
    """
    txt = ''
    for work_label in ALL_WORK_LABELS:
        copy_pdf_text = str(pdf_text)
        for prefix_label in HISTORY_LABELS:
            pattern = re.compile(prefix_label + '\\s'+ work_label+'*')
            if not prefix_label:
                pattern = re.compile(work_label+'*')
            match = pattern.search(copy_pdf_text)
            if not match:
                continue
            (start, _) = match.span()
            parsed_txt = copy_pdf_text[start:start + 1000]
            parsed_txt = re.sub('\n', '|', parsed_txt)
            copy_pdf_text = copy_pdf_text[start + 1000:]
            if parsed_txt:
                txt = txt + str(clean_text_values(parsed_txt)\
                        .encode("latin-1").decode()).strip() + MULTIPLE_SEGMENT_BREAK
    return txt

def extract_text_from_pdf(pdf_text, file_name):
    """
    Returns the extracted work information as a dictionary
    """
    work_data = dict()
    pdf_text = pdf_text.lower()

    work_text = extract_work_part(pdf_text)
    if work_text:
        work_data['file_name'] = file_name
        work_data['work'] = work_text
    return work_data


def extract_work_section(file_path, actual_file_name):
    """
    Opens the converted pdf to text file & tries to extract the work information with different unicodes.
    """
    reload(sys)
    sys.setdefaultencoding('latin-1')
    with open(file_path, 'r') as fp:
        try:
            pdf_text = str(fp.read())
            return extract_text_from_pdf(pdf_text, actual_file_name)
        except Exception:
            print traceback.print_exc()
            utility.write_to_text_file(CODEC_FAILURE, file_path+"','")

def main():
    """
    1. Fetches the pdf CV's from the given location
    2. Makes into chuck of 100 pdfs for processing.
    3. Converts the pdf to text file using the unix commad pdftotext
    3. Extracts the work information from the text file.
    4. Gives this information for further granular extraction of different categories
        a. Learning the order of these categories and filling blank if not available
        b. Plain extraction of the categories
    5. Maintains an exception list for catching all the different exception
    6. Many exception lists like no data, unmatched work information, error due to codecs are maintained
    """
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
                utility.convert_pdf_to_text(pdf)
                split_pdf_extension = os.path.splitext(pdf)
                (_, file_name) = os.path.split(pdf)

                # work scrapping
                work = extract_work_section(split_pdf_extension[0] + ".txt", file_name)
                if work:
                    work_list.append(work)
                    categorize_work_info(work, LOGIC_CODE_CATEGORY_LEARNING_NON_BOLD)
                    categorize_work_info(work, LOGIC_CODE_CATEGORY_PLAIN_PARSING_NON_BOLD)
                else:
                    work_error_list.append(file_name)
            except Exception:
                print traceback.print_exc()
                error_files.append(pdf)

        # Inserting the work information in chuncks
        work_file_path = os.path.join(WORK_FILE_PATH,\
            'work_cv_' + str(inital_count) + '_' + str(inital_count + 100) + '.txt')
        if work_list:
            utility.write_json_to_text_file(work_file_path, work_list)
        inital_count = inital_count + 101

    utility.write_json_to_text_file(UNMATCHED_WORK, work_error_list)
    utility.write_json_to_text_file(ERROR_FILE_PATH, error_files)
    update_possible_error_rows(LOGIC_CODE_CATEGORY_LEARNING_NON_BOLD,
                               LOGIC_CODE_CATEGORY_PLAIN_PARSING_NON_BOLD)


if __name__ == "__main__":
    main()
