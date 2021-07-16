import re

from olparse.utils import load_laws

# RNR
P_absatzRechts = re.compile('<span [^>]*class="absatzRechts">')
P_rd = re.compile('<a [^>]*name="rd_[\d]+">')
P_nr = re.compile('(<rd [^>]*nr="[\d]+"/>)')
P_point = re.compile('<p [^>]*id="point[\d]+">')

# LAWS
LAWS_SET = load_laws()
LAWS_STRING = "|".join(LAWS_SET)
P_vorschrift = re.compile(
    r"(?P<Vorschrift>%s|[A-Z][\-\w]+[gG]esetz[\-\w]*|[A-Z][\-\w]+[oO]rdnung[\-\w]*( [IVXLCDM]*)?)"
    % LAWS_STRING
)
P_simple = re.compile(r"( ?§ | ?Art\. | ?Artikel )[^§]{1,80}?" + P_vorschrift.pattern)
P_multi = re.compile(r"( ?§§ ).{1,80}?%s" % P_vorschrift.pattern)
P_split_ivm = re.compile(r" [iI]n?\.? ?[Vv](?:erbindung)?\.? ?[mM](?:it)?\.? ")
P_ivm = re.compile(
    r"( ?§ | ?Art. | ?Artikel | ?§§ )[^§]{1,60}%s.{1,60}%s"
    % (P_split_ivm.pattern, P_vorschrift.pattern)
)

# FILE
# P_file = re.compile(r" ?(\d+|[IVXLCDM]+)? ?\w+[ -]\d+[/.]\d+")
_az_kammer = r"(?P<kammer>\d{1,2}|[IVXLCDM]{1,4})"
_az_regz = r"(?P<regz>[A-Z][a-zA-Z]{0,6})"
_az_case = r"(?P<nr>\d+)[\.\/](?P<jahr>\d+)"
_az_pat = _az_kammer + r"[- ]?" + _az_regz + r"[- ]?" + _az_case
P_file = re.compile(_az_pat)
