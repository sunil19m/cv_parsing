
#
#   File currently not used
#

from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from cStringIO import StringIO

import codecs

import sys  

class Utility(object):

    def convert_pdf_to_txt(self, path, page_num=set(), max_pages=0):
        with codecs.open(path, 'rb', encoding="latin-1") as fp:
            reload(sys)  
            sys.setdefaultencoding('latin-1')
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

"""
from utility import Utility
from constant import PDF_FILE

utility = Utility()
print utility.convert_pdf_to_txt(PDF_FILE, page_num=[0])
"""