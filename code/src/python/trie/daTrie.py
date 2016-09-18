# -*- coding: latin-1 -*-
import os.path
import string


import datrie

from trie import Trie as T


class DaTrie(T):

    """
        Class to create a trie by providing the datab data.
        The trie is created on the all the columns in the datab data & the leaf node will be the key column of datab
        If multiple key columns in datab, it creates | and joins all the key columns.

        In case the user wants to customize the columns to be in trie & the leaf node. Then it can be provided
        by providing the
        trie_col_name_list -> List of columns on which trie must be created
        leaf_node_col -> Name of the column as a leaf node of the trie.

        Creates a trie if the word is greater than 3 Charaters and breaks on space.
    """

    def __init__(self):
        """
            Check if the datab key has Keys|Composite keys. If yes then create a single column with '|' appended values
            and make this column as the leaf_node_col
        """
        self._trie = datrie.Trie(string.printable +
                                 'ÁáÉéÍíÓóÚúÑñ'.decode('latin-1') +
                                 '\xc1\xc9\xcd\xd3\xda\xd1'.decode('latin-1') +
                                 '\xa1\xa0\xa2\xa5\xa4\xa7\xa6\xa8\xab\xaa\xac\xb1\xb0\xb2\xb5\xb4\
                                  \xb7\xb6\xb9\xb8\xbb\xba\xbd\xbe\xc0\xc3\xc2\xc5\xc4\xc7\xc8\xcb\
                                  \xca\xcc\xcf\xd1\xd0\xd2\xd4\xd6\xdc\xde\xe7\xed\xf1\xf3\xfc\
                                  \xe1,\xe9,\xdb,\xc5,\xbf\
                                  \x8a,\x8e,\x92,\x94,\x9e,\xc1,\xc9,\xce,\xd5,\xd8,\xda,\xdd'.decode('latin-1'))
       
    def put_to_trie(self, word, leaf_node):
        try:
            if word not in self._trie:
                self._trie.setdefault(word, set([]))
            existing_key = self._trie[word]
            existing_key.add(leaf_node)
            self._trie[word] = existing_key
        except Exception, e:
            print word + ' ---> ' + str(e)

    def fetch_from_trie(self, search_word):
        return self._trie.values(search_word)

    @property
    def trie(self):
        return self._trie

    @trie.setter
    def trie(self, value):
        self._trie = value

    #
    # Improvement
    #   1. Using the ABS redis function
    #   2. The hardcode file path for the serialized trie
    #

    @classmethod
    def deserialize_trie(self, cached_file_name):
        """
            Deserializes the trie
        """

        with open(cached_file_name, 'rb', 0) as f:
            return datrie.Trie.read(f)

    @classmethod
    def serialize_trie(self, cached_file_name, trie_obj):
        """
            Serializes the trie
        """

        with open(cached_file_name, 'wb', 0) as f:
            trie_obj.write(f)

    @classmethod
    def cache_datrie_to_file(self, file_path):
        """
        The trie to redis will do the following
            1. If the trie is not available in redis, tries to serialize the trie and write it to the appropriate path
                The file name will be the function name
            2. If the trie is available in the redis cache, then deserialize the trie from the appropriate path where
                it was earlier serialized
        """

        def wrapper_func(fn):

            def compute_trie(*args, **kwargs):
                cached_file_name = file_path + fn.__name__
                if os.path.isfile(cached_file_name):
                    return DaTrie.deserialize_trie(cached_file_name)
                else:
                    trie = fn(*args, **kwargs)
                    DaTrie.serialize_trie(cached_file_name, trie)
                    return trie

            return compute_trie

        return wrapper_func