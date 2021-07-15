import re

from olparse.utils import load_laws


LAWS_SET = load_laws()

LAWS_STRING = "|".join(LAWS_SET)
P_absatzRechts = re.compile('<span [^>]*class="absatzRechts">')
P_rd = re.compile('<a [^>]*name="rd_[\d]+">')
P_nr = re.compile('(<rd [^>]*nr="[\d]+"/>)')
P_point = re.compile('<p [^>]*id="point[\d]+">')
P_simple = re.compile(
    r"( ?§ | ?Art\. | ?Artikel ).{1,50}?(%s|[gG]esetz[-\w]*|[oO]rdnung[-\w]*)( [IVXLCDM]*)?"
    % LAWS_STRING
)
P_multi = re.compile(
    r"( ?§§ ).*?(%s|[gG]esetz[-\w]*|[oO]rdnung[-\w]*)( [IVXLCDM]*)?"
    % LAWS_STRING
)
P_ivm = re.compile(
    r"( ?§ | ?Art. | ?Artikel | ?§§ ).*?( [iI]\.? ?[Vv]\.? ?[mM]\.? ).*?(%s|[gG]esetz[-\w]*|[oO]rdnung[-\w]*)( [IVXLCDM]*)?"
    % LAWS_STRING
)
# P_file = re.compile(r" ?(\d+|[IVXLCDM]+)? ?\w+[ -]\d+[/.]\d+")
P_split_ivm = re.compile(r" [iI]\.? ?[Vv]\.? ?[mM]\.? ")

_az_kammer = r"(?P<kammer>\d{1,2}|[IVXLCDM]{1,4})"
_az_regz = r"(?P<regz>[A-Z][a-zA-Z]{0,6})"
_az_case = r"(?P<nr>\d+)[\.\/](?P<jahr>\d+)"
_az_pat = _az_kammer + r"?[- ]?" + _az_regz + r"[- ]?" + _az_case
P_file = re.compile(_az_pat)