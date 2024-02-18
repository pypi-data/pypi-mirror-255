from random import SystemRandom

import emojipasta.util.text
from emojipasta.data.emoji_mappings import default_emoji_mappings

cryptogen = SystemRandom()


def _get_alphanumeric_prefix(s):
    i = 0
    while i < len(s) and s[i].isalnum():
        i += 1
    return s[:i]


class Emojipasta:
    _WORD_DELIMITER = " "
    _MAX_EMOJIS_PER_BLOCK = 2

    @classmethod
    def of_default_mappings(cls):
        return Emojipasta(default_emoji_mappings)

    @classmethod
    def of_custom_mappings(cls, emoji_mappings):
        return Emojipasta(emoji_mappings)

    def __init__(self, emoji_mappings):
        self._emoji_mappings = emoji_mappings


    def generate_emojipasta(self, text):
        blocks = emojipasta.util.text.split_into_blocks(text)
        new_blocks = []
        for i, block in enumerate(blocks):
            new_blocks.append(block)
            emojis = self._generate_emojis_from(block)
            if emojis:
                new_blocks.append(" " + emojis)
        return "".join(new_blocks)

    def _generate_emojis_from(self, block):
        trimmed_block = emojipasta.util.text.trim_nonalphabetical_characters(block)
        matching_emojis = self._get_matching_emojis(trimmed_block)
        emojis = []
        if matching_emojis:
            num_emojis = cryptogen.randint(0, self._MAX_EMOJIS_PER_BLOCK)
            for _ in range(num_emojis):
                emojis.append(cryptogen.choice(matching_emojis))
        return "".join(emojis)

    def _get_matching_emojis(self, trimmed_block):
        key = _get_alphanumeric_prefix(trimmed_block.lower())
        if key in self._emoji_mappings:
            return self._emoji_mappings[_get_alphanumeric_prefix(key)]
        return []
