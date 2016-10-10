
#
#   File currently not used
#

from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from cStringIO import StringIO

import codecs

import os
from glob import glob
from BeautifulSoup import BeautifulSoup
import sys
import re
import json
import traceback


class Utility(object):

    def convert_pdf_to_txt(self, path, page_num=set(), max_pages=0):
        """
        utility.convert_pdf_to_txt(PDF_FILE, page_num=[0])
        """
        with codecs.open(path, 'rb', encoding="latin-1") as fp:
            rsrcmgr = PDFResourceManager()
            str_buffer = StringIO()
            laparams = LAParams()
            device = TextConverter(rsrcmgr, str_buffer, codec='latin-1', laparams=laparams)
            interpreter = PDFPageInterpreter(rsrcmgr, device)
            for page in PDFPage.get_pages(fp, pagenos=page_num, maxpages=max_pages,
                                          password="",caching=True, check_extractable=True):
                interpreter.process_page(page)

            text = str_buffer.getvalue()
            return text

    def fetch_pdf_files(self, file_path):
        result = glob(file_path + "*.pdf")
        if not result:
            raise Exception("The file path does not have any pdf files: "+ file_path)
        return result

    def convert_pdf_to_html(self, pdf_file):
        os.system('pdftohtml -f 1 -l 2 -q '+ pdf_file)

    def remove_html_png_jpg_create_files(self, file_path):
        os.system('\\rm '+ file_path +'*.png')
        os.system('\\rm '+ file_path +'*.jpg')
        os.system('\\rm '+ file_path +'*.html')

    def clean_text_values(self, text_value):
        text_value = re.sub('&amp;', '&', text_value, re.MULTILINE)
        text_value = re.sub('&#160;', ' ', text_value, re.MULTILINE)
        text_value = re.sub('#160;', ' ', text_value, re.MULTILINE)
        text_value = re.sub('160;', ' ', text_value, re.MULTILINE)
        text_value = re.sub('&#', ' ', text_value, re.MULTILINE)
        
        text_value = re.sub(r"\\\w+", " ", text_value, re.MULTILINE)
        text_value = re.sub('[^a-zA-Z0-9-_*.@(),& |]', ' ', text_value, re.MULTILINE)
        text_value = re.sub('\(', ',', text_value, re.MULTILINE)
        text_value = re.sub('\)', ',', text_value, re.MULTILINE)
        text_value = re.sub('&#160;', ' ', text_value, re.MULTILINE)
        return " ".join(text_value.split())

    def write_json_to_text_file(self, file_path, json_data):
        try:
            if json_data:
                with codecs.open(file_path, 'w', encoding="latin-1") as fp:
                    json.dump(json_data, fp)
                    fp.close()
        except:
            print file_path
            

    def write_to_text_file(self, file_path, data):
        if data:
            with codecs.open(file_path, 'a', encoding="latin-1") as fp:
                fp.write(data)
                fp.close()

    def read_from_json(self, file_path):
        with codecs.open(file_path, 'r', encoding="latin-1") as fp:
            return json.load(fp)

    def convert_pdf_to_text(self, pdf_file):
        os.system('pdftotext -f 1 -l 2 -q '+ pdf_file)