
# Edit the top directory based on your respository
TOP_DIRECTORY = "/media/sunil/Others"

DATA_DIRECTORY = TOP_DIRECTORY + "/cv_parsing/data"
PDF_FILE_PATH = DATA_DIRECTORY + "/NewCV/CV/"
#PDF_FILE_PATH = DATA_DIRECTORY + "/CV_trail/"


# Output directory path
OUTPUT_DIRECTORY = DATA_DIRECTORY + "/Output"
EDUCATION_FILE_PATH = OUTPUT_DIRECTORY + "/Education/"
NO_BOLD_CV_FILE_PATH = OUTPUT_DIRECTORY + "/no_bold_cv.txt"
ERROR_FILE_PATH = OUTPUT_DIRECTORY + "/error_cv.txt"
ALL_LABELS_CV_FILE_PATH = OUTPUT_DIRECTORY + "/all_bold_labels.txt"
UNMATCHED_EDUCATION_BOLD = OUTPUT_DIRECTORY + "/unmatched_education_bold.txt"
FAILED_EDUCATION_JSON_PARSE = OUTPUT_DIRECTORY + "/failed_education_json_parse.txt"

# Trie cache for university match
CACHE_DIRECTORY = TOP_DIRECTORY + '/cv_parsing/cache'

COLLEGE_INFO_PATH = DATA_DIRECTORY + '/university_list.json'
TRIE_PATH = CACHE_DIRECTORY + '/college_trie/'