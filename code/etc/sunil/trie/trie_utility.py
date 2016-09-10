import re


class TrieUtility(object):
    @classmethod
    def create_trie_from_dict(self, trie_class_obj, dict_input, min_word_len=3, pattern_break=r"[\s,']"):
        for key, value in dict_input.iteritems():
            leaf = key.upper()
            trie_words = re.split(pattern_break, value)
            for word in trie_words:
                if not len(word) >= min_word_len:
                    continue
                word = unicode(word.upper())
                trie_class_obj.put_to_trie(word, leaf)
        return trie_class_obj.trie


    @classmethod
    def search_from_trie(
        self,
        trie_class_obj,
        search_words,
        min_word_len=3,
        pattern_break=r"[\s,']",
        ):
        """   
            Get all the search results
            Each word is split on space & for each word the value set is taken
            trie_result = [set('Search result of ABC'), set('Search result of XYZ')], if search_word is 'ABC XYZ'
        """

        search_results = list()
        splt_words = re.split(pattern_break, search_words)
        for word in splt_words:
            if not len(word) >= min_word_len:
                continue
            result = trie_class_obj.fetch_from_trie(word)
            if result:
                res = list()
                for r in result:
                    res.extend(r)
                search_results.append(res)
            else:
                search_results.append(result)
        return search_results