"""
Utility module.

All the required utility functions for parsing the cv is part of this module.
"""
import codecs
import json
import os
import re
from cStringIO import StringIO
from collections import OrderedDict
from glob import glob

from BeautifulSoup import BeautifulSoup
import pandas as pd
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage



def convert_pdf_to_txt(path, page_num=None, max_pages=0):
    """
    This function uses pdfminer to convert the pdf files to text files.
    The data provided by the pdfminer was not of high quality. The pdftotext gave a
    better result in align the text in the proper line than pdf2text (pdfminer)
    Hence this utility is not used. We can use this if required to compare the pdftotext & pdf2text result
    utility.convert_pdf_to_txt(PDF_FILE, page_num=[0])
    """
    if not page_num:
        page_num = set()
    with codecs.open(path, 'rb', encoding="latin-1") as fp:
        rsrcmgr = PDFResourceManager()
        str_buffer = StringIO()
        laparams = LAParams()
        device = TextConverter(rsrcmgr, str_buffer, codec='latin-1', laparams=laparams)
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        for page in PDFPage.get_pages(fp, pagenos=page_num, maxpages=max_pages,
                                      password="", caching=True, check_extractable=True):
            interpreter.process_page(page)

        text = str_buffer.getvalue()
        return text

def fetch_pdf_files(file_path):
    """
    Given a file path, this function returns all the .pdf files available in that directory
    """
    result = glob(file_path + "*.pdf")
    if not result:
        raise Exception("The file path does not have any pdf files: "+ file_path)
    return result

def convert_pdf_to_html(pdf_file):
    """
    This system command converts the pdf to html starting from 1st page to 2nd page
    """
    os.system('pdftohtml -f 1 -l 2 -q '+ pdf_file)

def remove_pdf_residual_files(file_path):
    """
    This function is not used. Because its dangerous to delete the directory with *.png, *.jpg
    If there are any of these extension in the same pdf directory. This will be deleted.
    These files are generated when we use pdftohtml or pdftotext commands.
    """
    os.system('\\rm '+ file_path +'*.png')
    os.system('\\rm '+ file_path +'*.jpg')
    os.system('\\rm '+ file_path +'*.html')

def clean_text_values(text_value):
    """
    Pdf to html gives many encoded character. Removing those are very much required.
    This function normalizes the converted texts.
    """
    text_value = re.sub('&amp;', '&', text_value, re.MULTILINE)
    text_value = re.sub('&#160;', ' ', text_value, re.MULTILINE)
    text_value = re.sub('#160;', ' ', text_value, re.MULTILINE)
    text_value = re.sub('160;', ' ', text_value, re.MULTILINE)
    text_value = re.sub('&#', ' ', text_value, re.MULTILINE)

    text_value = re.sub(r"\\\w+", " ", text_value, re.MULTILINE)
    text_value = re.sub('[^a-zA-Z0-9-_*.@(),& |]', ' ', text_value, re.MULTILINE)
    text_value = re.sub('\\(', ',', text_value, re.MULTILINE)
    text_value = re.sub('\\)', ',', text_value, re.MULTILINE)
    text_value = re.sub('&#160;', ' ', text_value, re.MULTILINE)
    return " ".join(text_value.split())

def write_json_to_text_file(file_path, json_data):
    """
    Creates a new file and writes the json data into a text file.
    """
    try:
        if json_data:
            with codecs.open(file_path, 'w', encoding="latin-1") as fp:
                json.dump(json_data, fp)
                fp.close()
    except Exception:
        print file_path


def write_to_text_file(file_path, data):
    """
    Creates a new file if not exists and appends the given string to a text file.
    """
    if data:
        with codecs.open(file_path, 'a', encoding="latin-1") as fp:
            fp.write(data)
            fp.close()

def read_from_json(file_path):
    """
    Read from json text file and converts into a dictonary
    """
    with codecs.open(file_path, 'r', encoding="latin-1") as fp:
        return json.load(fp)

def convert_pdf_to_text(pdf_file):
    """
    This system command converts the pdf to text starting from 1st page to 2nd page
    """
    os.system('pdftotext -f 1 -l 2 -q '+ pdf_file)

def fetch_bold_header_contents(html, actual_file_name):
    """
        Given an HTML text input. This utility parses the information and segregates into different
        into different sections based on the bold headers. Each bold section is stored into a dictionary.
        This returns a dictionary of bold labels & it contents

        Example: result{'Education': "Studied at university of souther california bla.. bla..",
                        'file_name': "xyz.pdf"}
    """
    result = OrderedDict()
    soup = BeautifulSoup(html)
    bold = soup.find("b")
    if bold:
        old_bold_text = bold.text
        inside_bold_string = ''
        bold_heading = str(clean_text_values(old_bold_text).encode('utf-8')).strip()
        try:
            while old_bold_text == bold.text:
                bold = bold.next
        except Exception:
            pass
        while bold:
            cur_bold = BeautifulSoup(str(bold))
            old_bold_text = cur_bold.text
            if cur_bold.find("b"):
                old_bold_text = bold.text
                result[bold_heading] = str(clean_text_values(inside_bold_string).encode('utf-8')).strip()
                inside_bold_string = ''
                bold_heading = str(clean_text_values(cur_bold.text).encode('utf-8')).strip()

            else:
                if len(inside_bold_string) < 100000:
                    inside_bold_string = str(clean_text_values(inside_bold_string).encode('utf-8'))\
                    .strip() + "|" + str(clean_text_values(cur_bold.text).encode('utf-8')).strip()
            if bold:
                bold = bold.next
                while old_bold_text == bold:
                    bold = bold.next
            else:
                break
        result[bold_heading] = str(clean_text_values(inside_bold_string).encode('utf-8')).strip()
        result["file_name"] = actual_file_name
    return result

def convert_to_df(data_list):
    """
    Converts the given list of dictionary to dataframe
    """
    dframe = pd.DataFrame(data_list)
    #df_clean = df.where((pd.notnull(df)), None)
    df_clean = dframe.where((pd.notnull(dframe)), 0)
    return df_clean

def df_mismatch_identifier(parsed_data, reverse_parse):
    """
    This is currently not used. This compares oned dataframe with the other dataframe
    for the mismatch
    """
    dframe = pd.concat([parsed_data, reverse_parse])
    dframe = dframe.reset_index(drop=True)
    diff_rows = dframe.groupby(list(dframe.columns))
    diff_df_rows = [x[0] for x in diff_rows.groups.values() if len(x) == 1]
    return diff_df_rows