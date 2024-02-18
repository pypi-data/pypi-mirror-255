from __future__ import annotations

from collections.abc import Hashable
from typing import TypeVar

Data = TypeVar('Data', bound=Hashable)

FIRST, SECOND, THIRD, NOT = 1, 2, 4, 8
PARTS = [FIRST, SECOND, THIRD, NOT]

MAX_SENTENCE_CHARS = 800
SENTENCE_BREAK = '(...)'
GLOBAL = '!global'

WORD_BOUNDARY = r'\b'
WORD_BOUNDARY_CHAR = '~'
WORD_BREAK_CHARS = ' \t\n\r\'".,;:!?()[]{}-+*/\\'
