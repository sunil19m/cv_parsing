"""
    The parser script is used to parse the professors resume

    This module parses the education related information using the below logic.
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
                      EDUCATION_FILE_PATH,
                      LOGIC_CODE_CATEGORY_LEARNING_NON_BOLD,
                      LOGIC_CODE_CATEGORY_PLAIN_PARSING_NON_BOLD,
                      PDF_FILE_PATH,
                      UNMATCHED_EDUCATION_BOLD)

from education_cv_parsing import (categorize_education_info,
                                  update_possible_error_rows)
import utility

def clean_text_values(text_value):
    """
    The pdf when converted will have many special & hexadecimal characters.
    The function helps in removing those characters.
    """
    text_value = text_value.replace("\xc2\xa0", " ")
    text_value = text_value.replace("\xc2", " ")
    text_value = text_value.replace("\xa0", " ")
    text_value = re.sub('^[\\w\\s,|.\\d]', ' ', text_value)
    text_value = re.sub("[!~@#$%^&*();:<>?]", " ", text_value)
    return text_value

def extract_education_part(pdf_text):
    """
    1. All work labels have string such as Positions, work, appointment.
    2. Since we dont know where this part of the section ends it takes the first 1000 characters
    from where the it found the work matching pattern.
    5. Returns the string of work related information from the resume.
    """
    pattern = re.compile(r'education*')
    match = pattern.search(pdf_text)
    if not match:
        return None
    (start, _) = match.span()
    txt = pdf_text[start:start + 1000]
    txt = re.sub('\n', '|', txt)
    txt = str(clean_text_values(txt).encode("latin-1").decode()).strip()
    return txt

def extract_text_from_pdf(pdf_text, file_name):
    """
    Returns the extracted work information as a dictionary
    """
    edu_data = dict()
    pdf_text = pdf_text.lower()

    education_text = extract_education_part(pdf_text)
    if education_text:
        edu_data['file_name'] = file_name
        edu_data['education'] = education_text
    return edu_data


def extract_education_section(file_path, actual_file_name):
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
    education_error_list = list()
    error_files = list()

    pdf_files = utility.fetch_pdf_files(PDF_FILE_PATH)
    inital_count = 0
    final_count = (len(pdf_files) + 10)
    while inital_count <= final_count:
        print "Starting chuck " + str(inital_count) + " : " + str(inital_count + 100)
        education_list = list()

        for pdf in pdf_files[inital_count:inital_count+100]:
            print pdf
            try:
                utility.convert_pdf_to_text(pdf)
                split_pdf_extension = os.path.splitext(pdf)
                (_, file_name) = os.path.split(pdf)

                # Education scrapping
                education = extract_education_section(split_pdf_extension[0] + ".txt", file_name)
                if education:
                    education_list.append(education)
                    categorize_education_info(education, LOGIC_CODE_CATEGORY_LEARNING_NON_BOLD)
                    categorize_education_info(education, LOGIC_CODE_CATEGORY_PLAIN_PARSING_NON_BOLD)
                else:
                    education_error_list.append(file_name)
            except Exception:
                print traceback.print_exc()
                error_files.append(pdf)

        # Inserting the education information in chuncks
        education_file_path = os.path.join(EDUCATION_FILE_PATH, 'education_cv_'\
            + str(inital_count) + '_' + str(inital_count + 100)+'.txt')
        if education_list:
            utility.write_json_to_text_file(education_file_path, education_list)
        inital_count = inital_count + 101

    utility.write_json_to_text_file(UNMATCHED_EDUCATION_BOLD, education_error_list)
    utility.write_json_to_text_file(ERROR_FILE_PATH, error_files)
    update_possible_error_rows(LOGIC_CODE_CATEGORY_LEARNING_NON_BOLD,
                               LOGIC_CODE_CATEGORY_PLAIN_PARSING_NON_BOLD)

if __name__ == "__main__":
    main()
