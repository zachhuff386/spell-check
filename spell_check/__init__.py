import collections
import difflib
import time
import string
import re
import timeit
import heapq
import operator

DEFAULT_WORDS_PATH = 'words'
VOWELS = {'a', 'e', 'i', 'o', 'u', 'y'}
WORD_REG = re.compile(r'[a-z]+')
WORD_SETS_IGNORE = {'er', 'in', 'es'}
LEV_MAX = 5
LEV_DIFF_MAX = 2
LEV_MATCH_COUNT = 10

try:
    from levenshtein import distance as levenshtein
except ImportError:
    print 'WARNING: Failed to load levenshtein c module, performance', \
        'will be limited!'
    def levenshtein(s1, s2):
        # Code from https://en.wikibooks.org/
        # wiki/Algorithm_Implementation/Strings/Levenshtein_distance
        if len(s1) < len(s2):
            s1, s2 = s2, s1
        len_s2 = len(s2)
        if not len_s2:
            return len(s1)

        previous_row = xrange(len_s2 + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row

        return previous_row[-1]

class Counter(collections.Counter):
    def least_common(self, n=None):
        if n is None:
            return sorted(self.iteritems(), key=operator.itemgetter(1))
        return heapq.nsmallest(n, self.iteritems(), key=operator.itemgetter(1))

class SpellCheck:
    def __init__(self):
        self._words = set()
        self._word_sets = collections.defaultdict(lambda: set())

    def _add_match(self, matched_candidates, match, limit):
        if match in matched_candidates:
            return False
        matched_candidates.append(match)
        if len(matched_candidates) >= limit:
            return True

    def add_word(self, word):
        word = ''.join(WORD_REG.findall(word.lower()))
        if not word:
            return

        # Skip words that already exists
        if word in self._words:
            return
        self._words.add(word)

        # Store word in sets for each group of two letters
        # wake will be stored as:
        # self._word_sets['wa'] = {'wake'}
        # self._word_sets['ak'] = {'wake'}
        # self._word_sets['ke'] = {'wake'}
        for i in xrange(len(word) - 1):
            key = word[i] + word[i + 1]
            # Largest word sets can be safely ignored reducing the size
            # of the possible matches with little effect on the results
            if key not in WORD_SETS_IGNORE:
                self._word_sets[key].add(word)

    def read_file(self, file_path=DEFAULT_WORDS_PATH):
        with open(file_path) as words_file:
            for word in words_file.readlines():
                self.add_word(word)

    def get_matches(self, word, limit=3):
        word = ''.join(WORD_REG.findall(word.lower()))
        word_set = set(word)
        word_len = len(word)
        common_words = Counter()
        pre_candidates = []
        pre_post_candidates = []
        min_candidates = []
        matched_candidates = []
        candidates_lev = Counter()

        # Check if word exists
        if word in self._words:
            return [word]

        # Get all words from dict that have a common set of two letters while
        # counting the occurrence of each word
        for i in xrange(len(word) - 1):
            key = word[i] + word[i + 1]
            for match in self._word_sets[key]:
                common_words[match] += 1

        # Get the matches that have the most common occurrences
        max_count = None
        max_count_diff_max = None
        for match, count in common_words.most_common():
            # Limit the difference between the count of most common occurring
            # word to the count of the least common occurring word. This will
            # limit the size of the candidates and search more likely
            # candidates
            if max_count is not None:
                if max_count - count > max_count_diff_max:
                    break
            else:
                max_count = count
                max_count_diff_max = max(2, max_count / 2)

            # If the length of the match is different to the word by
            # LEV_MAX - 1 it is not possible to reach the required min
            # levenshtein value and the levenshtein calculation can be skipped
            if abs(len(match) - word_len) > LEV_MAX - 1:
                continue

            # Calculate the levenshtein value and add to counter
            lev_val = levenshtein(word, match)
            if lev_val > LEV_MAX:
                continue
            candidates_lev[match] = lev_val

        # Spelling errors commonly have matching first or last letters so
        # candidates with matching first and last then first letters will have
        # priority
        min_lev_val = None
        for candidate, lev_val in candidates_lev.least_common(LEV_MATCH_COUNT):
            candidate_set = set(candidate)

            # Ignore candidates that have a levenshtein value diference greater
            # then the max to skip checking the less likely candidates when
            # there is highly likely candidates available
            if min_lev_val is not None:
                if lev_val - min_lev_val > LEV_DIFF_MAX:
                    break
            else:
                min_lev_val = lev_val

            # Check for matching first letters
            if word[0] == candidate[0]:
                pre_candidates.append(
                    (candidate, candidate_set, lev_val))

                # Check for matching last letters
                if word[-1] == candidate[-1]:
                    pre_post_candidates.append(
                        (candidate, candidate_set, lev_val))

            # Add all candidates that have the lowest levenshtein value
            if lev_val == min_lev_val:
                min_candidates.append(
                    (candidate, candidate_set, lev_val))

        # First check candidates with matching first and last letters then
        # check candidates with mtaching last letters
        for candidates in (pre_post_candidates, pre_candidates,
                min_candidates):
            # If there is only one candidate return
            if len(candidates) == 1:
                if self._add_match(matched_candidates,
                        candidates[0][0], limit):
                    return matched_candidates

            # Score the candidates based on the levenshtein value and
            # the number of missing vowels vs missing non-vowels
            # Example, spell check of weke will return both wake and were
            # wake will be given a higher score because it contains a
            # missing vowel
            # {'w', 'a', 'k', 'e'} - {'w', 'e', 'k', 'e'} = {'a'}
            # {'w', 'e', 'r', 'e'} - {'w', 'e', 'k', 'e'} = {'r'}
            candidates_score = Counter()
            for candidate, candidate_set, lev_val in candidates:
                candidates_score[candidate] = lev_val
                for missing_char in candidate_set - word_set:
                    if missing_char in VOWELS:
                        candidates_score[candidate] -= 1
                    else:
                        candidates_score[candidate] += 1

            # Add the candidates ordered by score
            for candidate, vowel_count in candidates_score.least_common():
                if self._add_match(matched_candidates,
                        candidate, limit):
                    return matched_candidates

            for candidate, candidate_set, lev_val in candidates:
                if self._add_match(matched_candidates, candidate, limit):
                    return matched_candidates

        return matched_candidates

    def get_matches_timed(self, word, limit=3):
        start = time.time()
        matches = self.get_matches(word, limit=limit)
        return (time.time() - start, matches)
