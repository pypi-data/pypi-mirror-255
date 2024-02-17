import re, itertools, sys


all_chars = (chr(i) for i in range(sys.maxunicode))
control_chars = "".join(map(chr, itertools.chain(range(0x00, 0x20), range(0x7F, 0xA0))))
control_char_re = re.compile("[%s]" % re.escape(control_chars))

def remove_bin_chars(s: str) -> str:
    return control_char_re.sub("", s)

