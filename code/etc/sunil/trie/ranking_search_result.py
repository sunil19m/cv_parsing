from operator import itemgetter
from collections import OrderedDict


class FrequencySearchRanking(object):

    def __init__(self, trie_search_result, TOP_MATCH_RESULTS=50):
        self.search_results = trie_search_result
        self.TOP_MATCH_RESULTS = TOP_MATCH_RESULTS

    def frequency_search_results(self):
        """
        Frequency Search Result ()
            - From the search results for different words, find the frequency of the key
            - Take the TOP 100 results

        Eg: Search word is SUNIL MURALIDHARA.
            - Then if a key as both SUNIL & MURALIDHARA, then the frequency would be 2.
        """

        word_len = len(self.search_results)
        frequency_result_ord_dict = OrderedDict()

        # Handle empty result case

        if word_len == 0:
            return frequency_result_ord_dict

        search_res_list = list()
        for res in self.search_results:
            search_res_list.extend(list(res))
        search_res_list.sort()
        search_frequency_dict = dict()
        init_count = 1.0 / word_len
        count = init_count
        if len(search_res_list) >= 2:
            for i in xrange(1, len(search_res_list)):
                if search_res_list[i - 1] != search_res_list[i]:
                    search_frequency_dict[search_res_list[i - 1]] = \
                        count
                    count = init_count
                else:
                    count = count + init_count
            search_frequency_dict[search_res_list[-1]] = count
        elif len(search_res_list) == 1:
            search_frequency_dict[search_res_list[0]] = init_count

        #
        # 1. If the frequency search result is more than 100 (Default Top_Frequency_Result) then use the frequency
        #   search result as base
        # and narrow the results by the taking the top 100 results from the frequency search. Else apply
        # the equivalence search for all the results coming from the search results
        #

        for val in sorted(search_frequency_dict.items(),
                          key=itemgetter(1),
                          reverse=True)[:self.TOP_MATCH_RESULTS]:
            frequency_result_ord_dict[val[0]] = val[1]
        return frequency_result_ord_dict


class EquivalenceSimilaritySearchRanking(object):

    def __init__(self, search_words, TOP_MATCH_RESULTS=100):
        self.search_words = search_words
        self.TOP_MATCH_RESULTS = TOP_MATCH_RESULTS

    def equivalence_and_similarity_search_result(self, key_search_dict):
        """
            Break down the given word into pairs.
            Example:
                - Search word - SUNIL M
                - Complete Text - ANIL

            Then the alogrithm splits these words
                - SUNIL M- {'SU', 'UN', 'NI', 'IL', 'L ',' M'}
                - ANIL G - {'AN', 'NI', 'IL', 'L ', 'G '}

            Compares both these and uses the following formula
            Ranking = 2 * Intersection / (Number of pairs in 'SUNIL M') + (Number of pairs in 'ANIL G')
            Ranking = 2 * 3/ (6+5)

            Refer the following link for
            http://www.catalysoft.com/articles/StrikeAMatch.html
        """

        original_pair_list = self._word_letter_pairs(self.search_words)
        similarity_rank_dict = dict()
        top_equi_similar_dict = OrderedDict()
        for (key, value) in key_search_dict.iteritems():
            similarity_rank_dict[key] = \
                self._compareStrings(original_pair_list, value)
            
        for val in sorted(similarity_rank_dict.items(),
                          key=itemgetter(1),
                          reverse=True)[:self.TOP_MATCH_RESULTS]:
            top_equi_similar_dict[val[0]] = val[1]
        return top_equi_similar_dict

    def convert_datab_to_key_value_str_dict(self, datab, normalize_unicode=False):
        """
            Given a datab with key, then converts to a dict with row values seperated by space.

            m =[{'date':'20130823','ABS':100,'CMBS':2000},\
                {'date':'20130824', 'ABS':150 , 'CMBS':300}]
            tbl = Table.from_rows(m)
            tbl = tbl.rekey('date')

            print tbl
            index       date    ABS CMBS
            -----   ========   ---- ----
            0   20130823   100 2000
            1   20130824    150  300

            print convert_datab_to_key_value_str_dict(tbl)
            {'20130823': '20130823 100 2000', '20130824': '20130824 150 300'}
        """

        datab_row_details = dict()
        all_columns = datab.schema.keys()
        key_col = datab.schema.key_name[0]
        for row in datab.itervalues():
            value = str(row.__getattr__(all_columns[0]))
            for col in all_columns[1:]:
                value = value + ' ' + str(row.__getattr__(col))
            key = str(row.__getattr__(key_col))
            datab_row_details[key] = value
        return datab_row_details

    def _letter_pairs(self, string_val):
        """
            Gives the list of pair of letter for a given string
        """

        pairs = list()
        for i in xrange(0, len(string_val)):
            pairs.append(string_val[i:i + 2])
        return pairs

    def _word_letter_pairs(self, string_val):
        """
            Letter pair for words
        """

        all_pairs = list()
        words = string_val.split("\s")
        for word in words:
            if word == '':
                continue
            pairs_in_word = self._letter_pairs(word)
            for element in pairs_in_word:
                all_pairs.append(element)
        return all_pairs

    def _compareStrings(self, original_pair_list, fetched_word):
        """
            comparing the search string with the original string & adding the ranking value to it.
        """

        fetched_pair_list = self._word_letter_pairs(fetched_word)
        intersection = 0
        union = len(original_pair_list) + len(fetched_pair_list)
        for i in xrange(0, len(original_pair_list)):
            pair1 = original_pair_list[i]
            for j in xrange(0, len(fetched_pair_list)):
                pair2 = fetched_pair_list[j]
                if pair1 == pair2:
                    intersection += 1
                    fetched_pair_list.remove(fetched_pair_list[j])
                    break
        return 2.0 * intersection / union


class CombineFrequencyAndEquivalencRanking(object):

    def __init__(self, frequency_search_result, equivalence_search_result, TOP_MATCH_RESULTS=100):
        self.frequency_search_result = frequency_search_result
        self.equivalence_search_result = equivalence_search_result
        self.TOP_MATCH_RESULTS = TOP_MATCH_RESULTS

    def combine_frequency_and_equivalence_search_result(self):
        """
            Combining the frequency match & equivalence match and coming up with the best solution
            To give equal weightage to both the frequency & equivalence search.

            Ranking = (Frequency Search Result/ No. of words ) * Equivalence search ranking
        """

        probability_dict = dict()
        for (key, value) in self.equivalence_search_result.iteritems():
            if key not in self.frequency_search_result:
                continue
            probility_occurance = self.frequency_search_result.get(key) * value
            probability_dict[key] = probility_occurance
        top_ranked_combine_freq_equi_dict = OrderedDict()
        for val in sorted(probability_dict.items(), key=itemgetter(1),
                          reverse=True)[:self.TOP_MATCH_RESULTS]:
            top_ranked_combine_freq_equi_dict[val[0]] = val[1]
        return top_ranked_combine_freq_equi_dict
