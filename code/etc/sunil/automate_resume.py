from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from cStringIO import StringIO

from college_info_trie import possible_college_search


FILE_PATH = '/media/sunil/Others/project_marshall/resumes/Sunil_Muralidhara_Resume.pdf'

def convert_pdf_to_txt(path):
    with open(FILE_PATH, 'rb') as fp:
        rsrcmgr = PDFResourceManager()
        str_buffer = StringIO()
        laparams = LAParams()
        device = TextConverter(rsrcmgr, str_buffer, codec='utf-8', laparams=laparams)
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        for page in PDFPage.get_pages(fp, pagenos=set(), maxpages=0, password="",caching=True, check_extractable=True):
            interpreter.process_page(page)

        text = str_buffer.getvalue()
        return text

pdf_text = convert_pdf_to_txt(FILE_PATH)

print "======================================================================================="
import re
def full_name(pdf_text):
    """
    Making an assumption that the name is always at the top of the resume.
    """
    match = re.search(r'[\w\.\s]+', pdf_text)
    res = match.group(0)
    result = res.split("\n")[0]
    return result.strip()
print "Full Name: ", full_name(pdf_text)
print "======================================================================================="

def fetch_email_id(pdf_text):
    """
    Making an assumption that the email id matching string found 
    at the begining is the candidates email id.
    """
    match = re.search(r'[\w\.-]+@[\w\.-]+', pdf_text)
    return match.group(0) if match and match.group(0) else ''
print "Email ID: ", fetch_email_id(pdf_text)
print "======================================================================================="

def phone_number(pdf_text):
    """
    Making an assumption that the first phone number matching pattern found 
     is the candidates phone number.
    """
    pattern = "(\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4})"
    match = re.search(pattern, pdf_text)
    return match.group(0) if match and match.group(0) else ''
print "Phone Number: ", phone_number(pdf_text)
print "======================================================================================="

def postal_code(pdf_text):
    pattern = r'.*(\d{5}(\-\d{4})?)'
    match = re.search(pattern, pdf_text)
    return match.group(0) if match and match.group(0) else ''
print "Postal Code: ", postal_code(pdf_text)
print "======================================================================================="


def cleanse_words_from_pdf(pdf_text):
    pdf_text_lower = pdf_text.lower()
    pdf_text_space_comma_split = []
    pdf_text_comma_split = pdf_text_lower.split(',')
    for word in pdf_text_comma_split:
        pdf_text_space_comma_split.extend(word.split())
    return pdf_text_space_comma_split

def cleanse_words_from_required_skills(requied_skills):
    requied_skills_comma_split = []
    for word in requied_skills:
        words_lower = word
        words = words_lower.split()
        requied_skills_comma_split.extend(words)
    return requied_skills_comma_split

"""
Removing of special characters not requried. Eg. C#
def cleanse_words_from_list(word_list):
    cleansed_word_list = []
    for word in word_list:
        lower_word = word.lower()
        cleansed_word_list.append(''.join(x for x in lower_word if x.isalnum()))
    return cleansed_word_list
"""

requied_skills = ['Python', 'SQL Server', 'JavaScript', 'Jquery', 'Java', 'JSP', 'JSON', 'HTML5', 'Redis', 'Highchart', 
'UNIX', 'Linux', 'Struts2', 'Springs', 'Eclipse', 'Jenkins', 'XML', 'Sqlalchemy', 'Slickgrid', 'Ibatis', 
'R', 'C', 'C++', 'Perl', 'Oracle', 'Windows', 'C#', 'ASP.NET', 'WPF', 'ADO.Net', 'BigData', 'Hadoop', 'MongoDB']

def check_skill_set(pdf_text, requied_skills):
    matched_skills = []
    unmatched_skills = []
    pdf_text_space_split = cleanse_words_from_pdf(pdf_text)
    for skills in cleanse_words_from_required_skills(requied_skills):
        skills_lower = skills.lower()
        for word in pdf_text_space_split:
            if word == skills_lower:
                matched_skills.append(skills)
                break
        else:
            unmatched_skills.append(skills)
    return (matched_skills, unmatched_skills)

(matched_skills, unmatched_skills) = check_skill_set(pdf_text, requied_skills)
print "Matched Skills: ", matched_skills
print "Unmatched Skills: ", unmatched_skills
print "======================================================================================="


from collections import OrderedDict
from operator import itemgetter
def possible_colleges(pdf_text):
    possible_college_rank = list()
    pdf_text_split_on_new_line = pdf_text.split("\n")
    for line in pdf_text_split_on_new_line:
        word_list = line.split(",")
        for words in word_list:
            input_string = words.strip()
            possible_college_rank = possible_college_search(input_string, possible_college_rank)
                
    top_ranked_college_list = OrderedDict()
    for val in sorted(possible_college_rank, key=itemgetter(1),
                          reverse=True)[:5]:
        top_ranked_college_list[val[0]] = val[1]
    return top_ranked_college_list
    
print "Closet match college from resumes are"
for college, rank in possible_colleges(pdf_text).items():
    print college, " ", rank
print "======================================================================================="


