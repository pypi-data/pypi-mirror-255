from __future__ import annotations

from collections import defaultdict
from collections.abc import Generator
from collections.abc import Iterable
from copy import deepcopy
from typing import Generic

import search_string.constants as const
from search_string.constants import Data
from search_string.search_string import SearchString


class Trie(Generic[Data]):
    __slots__ = ('end_tokens', 'sub_tries')

    def __init__(
        self,
        sub_tries: dict[str, Trie[Data]] | None = None,
        end_tokens: set[tuple[Data, int]] | None = None,
    ) -> None:
        self.sub_tries: dict[str, Trie[Data]] = sub_tries or {}
        self.end_tokens: set[tuple[Data, int]] | None = end_tokens

    def __reduce__(
        self,
    ) -> tuple[
        type[Trie[Data]], tuple[dict[str, Trie[Data]], set[tuple[Data, int]] | None]
    ]:
        return self.__class__, (self.sub_tries, self.end_tokens)

    def __getitem__(self, key: str) -> Trie:
        return self.sub_tries[key]

    def __setitem__(self, key: str, value: Trie) -> None:
        self.sub_tries[key] = value

    def __contains__(self, char: str) -> bool:
        return char in self.sub_tries

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, Trie)
            and self.sub_tries == other.sub_tries
            and self.end_tokens == other.end_tokens
        )

    def get_or_insert(self, key: str) -> Trie[Data]:
        return self.sub_tries.setdefault(key, Trie())

    def add_end_token(self, token: tuple[Data, int]) -> None:
        if self.end_tokens is None:
            self.end_tokens = {token}
        else:
            self.end_tokens.add(token)

    @property
    def has_children(self) -> bool:
        return len(self.sub_tries) > 0


class SearchStringCollection(Generic[Data]):
    __slots__ = ('search_strings', 'trie')

    def __init__(
        self,
        search_strings: Iterable[SearchString[Data]],
        trie: Trie[Data] | None = None,
    ) -> None:
        self.search_strings = self._build_search_string_dict(search_strings)
        self.trie: Trie[Data] = trie or self._build_trie()

    def __reduce__(
        self,
    ) -> tuple[
        type[SearchStringCollection[Data]], tuple[list[SearchString[Data]], Trie[Data]]
    ]:
        return self.__class__, (list(self), self.trie)

    def __iter__(self) -> Generator[SearchString[Data], None, None]:
        yield from self.search_strings.values()

    def __repr__(self) -> str:
        if len(self) >= 4:
            return f'{self.__class__.__name__}({len(self)} search strings)'

        return f'{self.__class__.__name__}({list(self.search_strings.values())})'

    def __getitem__(self, key: Data) -> SearchString[Data]:
        return self.search_strings[key]

    def __len__(self) -> int:
        return len(self.search_strings)

    def _build_search_string_dict(
        self,
        search_strings: Iterable[SearchString[Data]],
    ) -> dict[Data, SearchString[Data]]:
        out_dict: dict[Data, SearchString[Data]] = {}
        for i, ss in enumerate(search_strings):
            if ss.data is None:
                raise ValueError(
                    f'Error with SearchString located at index {i}. '
                    + 'SearchStringCollection does not support search strings '
                    + 'with data=None',
                )
            if ss.data in out_dict:
                raise ValueError(
                    f'Error with SearchString located at index {i}. '
                    + 'The data property of all supplied search strings must '
                    + 'be unique but received duplicate value '
                    + f'data={ss.data!r}',
                )
            out_dict[ss.data] = ss
        return out_dict

    def _concat_matched_sentences(
        self,
        sentences: list[str],
        matched_sentence_indices: list[int],
        match_extract_max_sentences: int,
    ) -> list[str]:
        """
        Returns a list of sentences that contain the matched search strings
        and a SENTENCE_BREAK between sentences that are not matched.
        It is expected that `matched_sentence_indices` is in sorted order.
        """
        matched_sentences = []
        last_idx: int | None = None
        n_added_sentences = 0
        for sentence_index in matched_sentence_indices:
            if last_idx is not None and sentence_index - last_idx > 1:
                matched_sentences.append(const.SENTENCE_BREAK)

            sentence = sentences[sentence_index]
            matched_sentences.append(sentence[: const.MAX_SENTENCE_CHARS])
            last_idx = sentence_index
            n_added_sentences += 1
            if n_added_sentences >= match_extract_max_sentences:
                n_additional = len(matched_sentence_indices) - n_added_sentences
                if n_additional > 0:
                    matched_sentences.append(const.SENTENCE_BREAK)
                    sentences_str = (
                        'yderlig sætning'
                        if n_additional == 1
                        else 'yderligere sætninger'
                    )
                    msg = f'Søgeordet blev matchet i {n_additional} {sentences_str}.'
                    matched_sentences.append(msg)

                break

        return matched_sentences

    def _split_part(self, part: str) -> list[str]:
        cleaned = part.strip(' ;')
        if cleaned.endswith(const.GLOBAL):
            cleaned = cleaned[: -len(const.GLOBAL)]
        cleaned = cleaned.strip(' ;')

        parts = [p.strip() for p in cleaned.split(';')]
        return [p for p in parts if p]

    def _build_trie(self) -> Trie[Data]:
        root_trie: Trie[Data] = Trie()
        for ss in self:
            for part_id, part_str in ss._raw_parts():
                token = (ss.data, part_id)
                for splitted_part in self._split_part(part_str):
                    # Reverse the list of characters so we can pop in O(1)
                    rem_chars = list(splitted_part)[::-1]
                    active_trie = root_trie
                    while rem_chars:
                        cur_char = rem_chars.pop()
                        active_trie = active_trie.get_or_insert(cur_char)
                        if not rem_chars:
                            active_trie.add_end_token(token)
        return root_trie

    def _text_yielder(self, text: str) -> Generator[str, None, None]:
        """
        Yield the text surrounded with chars that will be treated as word
        boundaries.
        """
        yield '\n'  # Possible beginning word break
        yield from text
        yield '\n'  # Possible ending word break
        yield '\n'  # Strings that matched the end and need one more char to get added

    def _match_single_text(self, text: str) -> set[tuple[Data, int]]:
        """
        Matches a single text against the search strings and returns a set of
        tuples of the form (search_string_id, part_id).
        """
        cur_positions: list[Trie[Data]] = []
        matched: set[tuple[Data, int]] = set()
        for char in self._text_yielder(text):
            is_wb = char in const.WORD_BREAK_CHARS
            chars_to_check = [char, const.WORD_BOUNDARY_CHAR] if is_wb else [char]
            new_positions: list[Trie[Data]] = []
            cur_positions.append(self.trie)
            for char_to_check in chars_to_check:
                for cur_position in cur_positions:
                    if char_to_check not in cur_position:
                        continue

                    new_trie = cur_position[char_to_check]
                    if new_trie.has_children:
                        new_positions.append(new_trie)
                    if new_trie.end_tokens is not None:
                        matched.update(new_trie.end_tokens)
            cur_positions = new_positions
        return matched

    def _match_sentence(self, sentence: str) -> list[SearchString[Data]]:
        """
        Match the search strings against the text and return a list of
        SearchString objects that matched the text.
        """
        matched = self._match_single_text(sentence.lower())
        ssid_bitstrings: defaultdict[Data, int] = defaultdict(int)
        for ss_id, part_id in matched:
            ssid_bitstrings[ss_id] += part_id

        matched_ss: list[SearchString[Data]] = []
        for ss_id, bitstring in ssid_bitstrings.items():
            ss = self.search_strings[ss_id]
            if bitstring == ss.match_bitstring:
                ss.matched_sentences = [sentence[: const.MAX_SENTENCE_CHARS]]
                matched_ss.append(ss)
        return matched_ss

    def _match_sentences(self, sentences: list[str]) -> list[SearchString[Data]]:
        """
        Match the search strings against the text and return a list of
        SearchString objects that matched the text.
        """
        sentences_lower = [s.lower() for s in sentences]
        all_text = '\n'.join(sentences_lower)
        global_matched_raw = self._match_single_text(all_text)
        global_matched = {
            (ss_id, part_id)
            for ss_id, part_id in global_matched_raw
            if self.search_strings[ss_id].is_global(part_id)
        }
        global_ssid_bitstrings: defaultdict[Data, int] = defaultdict(int)
        for ss_id, part_id in global_matched:
            global_ssid_bitstrings[ss_id] += part_id

        matched_ssids: defaultdict[Data, list[int]] = defaultdict(list)
        for i, sentence in enumerate(sentences_lower):
            local_ssid_bitstrings = deepcopy(global_ssid_bitstrings)
            for ss_id, part_id in self._match_single_text(sentence):
                local_ssid_bitstrings[ss_id] += part_id

            for ss_id, bitstring in local_ssid_bitstrings.items():
                ss = self.search_strings[ss_id]
                if bitstring == ss.match_bitstring:
                    matched_ssids[ss_id].append(i)

        matched_ss: list[SearchString[Data]] = []
        for ss_id, sentence_ids in matched_ssids.items():
            ss = self.search_strings[ss_id]
            ss.matched_sentences = self._concat_matched_sentences(
                sentences, sentence_ids, ss.match_extract_max_sentences
            )
            matched_ss.append(ss)

        return matched_ss

    def find_all(self, text: str | list[str]) -> list[SearchString[Data]]:
        """
        Finds all matches of the search strings for the text or list of text
        fragments. Returns a list of the matched searchstrings. If none is found,
        the list is empty. Should be used when there can be multiple matches.

        Example:
        >>> ss = [SearchString('test', str(i), '', data=i) for i in range(500)]
        >>> results = SearchString.find_all(['test 12', 'test 9'], ss)
        >>> [(r.data, r.matched_text) for r in results]
        [(1, 'test 12'), (2, 'test 12'), (9, 'test 9'), (12, 'test 12')]
        """
        return (
            self._match_sentences(text)
            if isinstance(text, list)
            else self._match_sentence(text)
        )

    def find_one(self, text: str | list[str]) -> SearchString[Data] | None:
        """
        Finds the first match of the search strings for the text or list of
        text fragments and returns the given search string. If no match is
        found, None is returned. Should be used when there logically only can
        be one match.

        Example:
        >>> ss = [SearchString('test', str(i), '', data=i) for i in range(500)]
        >>> result = SearchString.find_one('test 123', ss)
        >>> result.data if result else None
        1
        >>> result.matched_text if result else None
        'test 123'
        """
        res = self.find_all(text)
        return res[0] if res else None

    def find_all_sliding_window(
        self,
        text: str,
        *,
        window_size: int = 300,
        step_size: int = 20,
    ) -> list[SearchString[Data]]:
        """
        Find matches based on a sliding window method. Can be used if
        underlying text is unsuitable for section- or sentence-tokenization
        but it should still be enforced that matched text parts are not too
        far apart.
        Returns a list of all the search strings that matched some window
        of the supplied text.
        You can tune the sliding window using the `window_size` and
        `step_size` parameters.

        Example:
        >>> ss = [SearchString('part1', 'part2', 'bad', data=None)]
        >>> ss_col = SearchStringCollection(ss)
        >>> text = (' ' * 200).join(['part1', 'part2', 'bad.'])
        >>> SearchStringCollection.find_all_sliding_window(text, window_size=100)
        []
        >>> SearchStringCollection.find_all_sliding_window(text, window_size=250)
        [SearchString(part1, part2, bad)]
        >>> SearchStringCollection.find_all_sliding_window(text, window_size=500)
        []
        """
        return self.find_all([
            text[start_idx : start_idx + window_size]
            for start_idx in range(0, len(text), step_size)
        ])
