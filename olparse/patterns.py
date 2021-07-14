import re

from olparse.utils import load_laws


LAWS_SET = load_laws()

LAWS_STRING = "|".join(LAWS_SET)
P_absatzRechts = re.compile('<span [^>]*class="absatzRechts">')
P_rd = re.compile('<a [^>]*name="rd_[\d]+">')
P_nr = re.compile('(<rd [^>]*nr="[\d]+"/>)')
P_point = re.compile('<p [^>]*id="point[\d]+">')
P_simple = re.compile(
    r"([ ]?§ |[ ]?Art[.] |[ ]?Artikel ).*?((\d|\w)+/)*(%s|[gG]esetz[-\w]*|[oO]rdnung[-\w]*)(/(\d|\w)+)*( [IVXLCDM]*)?"
    % LAWS_STRING
)
P_multi = re.compile(
    r"([ ]?§§ ).*?((\d|\w)+/)*(%s|[gG]esetz[-\w]*|[oO]rdnung[-\w]*)(/(\d|\w)+)*( [IVXLCDM]*)?"
    % LAWS_STRING
)
P_ivm = re.compile(
    r"([ ]?§ |[ ]?Art[.] |[ ]?Artikel |[ ]?§§ ).*?( [iI][.]?[Vv][.]?[mM][.]? ).*?((\d|\w)+/)*(%s|[gG]esetz[-\w]*|[oO]rdnung[-\w]*)(/(\d|\w)+)*( [IVXLCDM]*)?"
    % LAWS_STRING
)
P_file = re.compile(r"[ ]?(\d+|[IVXLCDM]+) \w+ \d+[/.]\d+")
P_split_ivm = re.compile(r" [iI][.]?[Vv][.]?[mM][.]? ")
