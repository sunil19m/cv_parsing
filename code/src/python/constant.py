
# Edit the top directory based on your respository
TOP_DIRECTORY = "/media/sunil/Others"

DATA_DIRECTORY = TOP_DIRECTORY + "/cv_parsing/data"
PDF_FILE_PATH = DATA_DIRECTORY + "/CV/"
#PDF_FILE_PATH = DATA_DIRECTORY + "/Tested_Fine/"


# Output directory path
OUTPUT_DIRECTORY = DATA_DIRECTORY + "/Output"
EDUCATION_FILE_PATH = OUTPUT_DIRECTORY + "/Education/"
NO_BOLD_CV_FILE_PATH = OUTPUT_DIRECTORY + "/no_bold_cv.txt"
ERROR_FILE_PATH = OUTPUT_DIRECTORY + "/error_cv.txt"
ALL_LABELS_CV_FILE_PATH = OUTPUT_DIRECTORY + "/all_bold_labels.txt"
UNMATCHED_EDUCATION_BOLD = OUTPUT_DIRECTORY + "/unmatched_education_bold.txt"
FAILED_EDUCATION_JSON_PARSE = OUTPUT_DIRECTORY + "/failed_education_json_parse.txt"
CODEC_FAILURE = OUTPUT_DIRECTORY + "/codec_failure.txt"

# Trie cache for university match
CACHE_DIRECTORY = TOP_DIRECTORY + '/cv_parsing/cache'

COLLEGE_INFO_PATH = DATA_DIRECTORY + '/university_list.json'
TRIE_PATH = CACHE_DIRECTORY + '/college_trie/'


# Education constants
NOISE_WORDS = ['economics', 'business', 'management', 'university', 'graduate', "education", "administration"]

DEGREE_META_DATA = ['ph.d.', 'ph.d', 'phd', 'doctor', 'ph. d.', 'doctorate'
    ,'m.s.', 'm.s', 'ms', 'm. s', 'm. s.'
    ,'m.a.', 'm.a', 'ma', 'master','masters'
    ,'m.b.a.', 'm.b.a', 'mba'
    ,'m.sc.', 'msc', 'm.s.c'
    ,'m.phil', 'm.phil.', 'mphil', 'm. phil.', 'm. phil', 'm phil.', 'm phil', 'mphil.'
    ,'d.phil', 'd.phil.', 'dphil', 'd. phil.', 'd. phil', 'd phil.', 'd phil'
    ,'m.ec.', 'mec', 'm.ec'
    ,'b.s.', 'b.s', 'bs',  'bachelor', 'b. s.'
    ,'b.sc.', 'bsc', 'b.sc'
    ,'b.ec.', 'bec', 'b.ec'
    ,'b.e.', 'b.e'
    ,'b.a.', 'b.a', 'ba'
    ,'b.b.m.', 'bbm', 'b.b.m', 'bbm.'
    ,'b.b.a.', 'bba', 'b.b.a', 'bba.'
    ,'b. comm.', 'b.comm.', 'b.comm', 'b. comm'
    ,'b.eng.', 'b.eng'
    ,'sc.b.', 'sc.b'
    ,'a.b.', 'a.b', 'ab'
    ,'j.d.','jd', 'j.d'
    ,'s.m.', 's.m'
    ,'s.b.', 's.b'
    ,'b.a.s.', 'b.a.s'
    ,'b.s.e.e.', 'b.s.e.e', 'bsee'
    ,'b.a.e.', 'b.a.e'
    ,'laurea'
    ,'b.s.b.a.', 'b.s.b.a'
    ,'b.s.e.', 'b.s.e'
    ]

MORE_DEGREES = ['habilitation', 'general', 'licentiate', 'a.a.s.', 'graduate tax']

MORE_COLLEGES = [
    {"country": "NA", "name": "UNIVERSITY OF ST. GALLEN"},
    {"country": "NA", "name": "STANFORD GRADUATE SCHOOL OF BUSINESS"},
    {"country": "NA", "name": "LONDON SCHOOL OF ECONOMICS"},
    {"country": "NA", "name": "M.I.T"},
    {"country": "NA", "name": "M.I.T."},
    {"country": "NA", "name": "MIT"},
    {"country": "NA", "name": "U.L.B"},
    {"country": "NA", "name": "columbia university"},
    {"country": "NA", "name": "Moscow Institute for Physics and Engineering"},
    # {"country": "NA", "name": "Haas School of Business"},
    {"country": "NA", "name": "dauphine"},
    {"country": "NA", "name": "universidad simon bolivar"},
    {"country": "NA", "name": "University of Bern"},
    {"country": "NA", "name":"Cranfield Institute of Technology"},
    {"country": "NA", "name":"University of Bombay"},
    {"country": "NA", "name":"norwegian university of science and technology"},
    {"country": "NA", "name":"Virginia Polytechnic"},
    {"country": "NA", "name":"Nuffield College"},
    {"country": "NA", "name":"University of Chile"},
    {"country": "NA", "name":"THE PENNSYLVANIA STATE UNIVERSITY"},
    {"country": "NA", "name":"Universite Toulouse"},
    {"country": "NA", "name":"Delhi University"},
    {"country": "NA", "name":"Delhi School of Economics"},
    {"country": "NA", "name":"Indian Institute of Management, Ahmedabad"},
    {"country": "NA", "name":"University of Vienna"},
    {"country": "NA", "name":"Institute for Advanced Studies, Vienna"},
    {"country": "NA", "name":"Toulouse University"},
    {"country": "NA", "name":"Universit Bocconi"},
    {"country": "NA", "name":"Istituto Universitario Navale"},
    {"country": "NA", "name":"Cambridge University"},
    {"country": "NA", "name":"Lund University"},
    {"country": "NA", "name":"Stockholm School of Economics"},
    # {"country": "NA", "name":"Kellogg Graduate School of Management"},
    {"country": "NA", "name":"University of Illinois"},
    {"country": "NA", "name":"University of Texas"},
    {"country": "NA", "name":"University of Wisconsin"},
    {"country": "NA", "name":"University of Hawaii"},
    {"country": "NA", "name":"Universit Toulouse"},
    {"country": "NA", "name":"University of AmsterdamUniversity of Pisa"},
    {"country": "NA", "name":"Indian Institute of Management, Calcutta"},
    {"country": "NA", "name":"Beijing University"},
    {"country": "NA", "name":"Southern Illinois University"},
    {"country": "NA", "name":"University of Texas Austin"},
    {"country": "NA", "name":"Columbia Business School"},
    {"country": "NA", "name":"University of Fribourg"},
    {"country": "NA", "name":"Virginia Tech"},
    {"country": "NA", "name":"University of Aarhus"},

    {"country": "NA", "name":"Bocconi University"},
    {"country": "NA", "name":"University of Illinois, Champaign Urbana"},
    {"country": "NA", "name":"University of Zagreb"},
    {"country": "NA", "name":"Iowa State University"},
    {"country": "NA", "name":"West Virginia University"},
    {"country": "NA", "name":"INSEAD,"},
    {"country": "NA", "name":"S.U.N.Y. Binghamton"},
    {"country": "NA", "name":"tilburg university"},
    {"country": "NA", "name":"university of ferrara"},
    {"country": "NA", "name":"University of Western Australia"}
]
