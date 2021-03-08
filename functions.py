import re
import json
from bs4 import BeautifulSoup
import models as ms


ROMAN_ARABIC_MAP = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}
LAWS_SET = set()
try:
    LAWS_SET.update([x.strip() for x in open("laws.txt", "r").readlines()])

except Exception:
    print("laws.txt file is missing")
    exit()


def is_roman(s):
    if re.search(r"[^IVXLCDM]+", s):
        return False

    return True


def roman_to_arabic(s):
    result, offset, add = 0, 0, True
    for i in range(len(s)):
        if offset > 0:
            offset -= 1
            continue

        for j in range(i+1, len(s)):
            if ROMAN_ARABIC_MAP[s[j]] == ROMAN_ARABIC_MAP[s[i]]:
                offset += 1

            elif ROMAN_ARABIC_MAP[s[j]] > ROMAN_ARABIC_MAP[s[i]]:
                add = False
                break

            else:
                break

        if add:
            result += (offset+1) * ROMAN_ARABIC_MAP[s[i]]

        else:
            result -= (offset+1) * ROMAN_ARABIC_MAP[s[i]]

        add = True

    return str(result)


def is_simple(s):
    return s.count("§") == 1 or re.match(r"[Aa]", s)


def is_multi(s):
    return s.count("§") == 2


def get_vorschrift_from_simple(s):
    try:
        result = s.split(" ")
        if is_roman(result[-1]):
            return result[-2]

        return result[-1]

    except Exception:
        raise ms.ReferenceObjectException()


def get_buch_from_simple(s):
    try:
        result = s.split(" ")[-1]
        if is_roman(result):
            return result

        return ""

    except Exception:
        raise ms.ReferenceObjectException()


def get_paragraph_from_simple(s):
    if re.search(r"-|f[.]", s):
        raise ms.ReferenceObjectException()

    try:
        result = s.split(" ")
        if is_roman(result[1]):
            return roman_to_arabic(result[1])

        if re.match(r"[a-z]\b", result[2]):
            return "".join(result[1:3])

        return result[1]

    except Exception:
        raise ms.ReferenceObjectException()


def get_abs_from_simple(s):
    try:
        return re.split(r" [Aa]bs[.] | [Aa]bsatz ", s)[1].split(" ")[0]

    except Exception:
        result, relevant_idx = s.split(" "), 2
        if re.match(r"[a-z]\b", result[relevant_idx]):
            relevant_idx += 1

        if is_roman(result[relevant_idx]):
            return roman_to_arabic(result[relevant_idx])

        if result[relevant_idx].startswith("(") and result[relevant_idx].endswith(")"):
            return result[relevant_idx][1:-1]

        return ""


def get_satz_from_simple(s):
    try:
        return re.split(r" [Ss][.] | [Ss]atz ", s)[1].split(" ")[0]

    except Exception:
        result, relevant_idx = s.split(" "), 2
        if re.match(r"[a-z]\b", result[relevant_idx]):
            relevant_idx += 1

        if is_roman(result[relevant_idx]) or result[relevant_idx].startswith("(") and result[relevant_idx].endswith(")"):
            relevant_idx += 1

        if re.match(r"[0-9]+\b", result[relevant_idx]):
            return result[relevant_idx]

        return ""


def get_nr_from_simple(s):
    try:
        return re.split(r" [Nn]r[.] | [Nn]ummer | [lL]it[.] | [Ss]piegelstrich | [Bb]uchst[.] | [Bb]uchstabe ", s)[1].split(" ")[0]

    except Exception:
        return ""


def get_lawrefs_from_multi(s):
    try:
        vorschrift, buch = get_vorschrift_from_simple(s), get_buch_from_simple(s)
        if buch != "":
            suffix = "%s %s" % (vorschrift, buch)
        else:
            suffix = vorschrift

        _split, result = s[3:].split(", "), list()
        for x in _split:
            if re.search(r"-|\bund\b", x):
                continue

            try:
                result.append(ms.SimpleLawRef("§ %s %s" % (x, suffix)))

            except Exception:
                pass

        return result

    except Exception:
        raise ms.ReferenceObjectException()


def get_left_from_ivm(s):
    try:
        result, law_complement = re.split(r" [iI][.]?[Vv][.]?[mM][.]? ", s), ""
        if result[0].split(" ")[-1] not in LAWS_SET:
            law_complement = result[1].split(" ")[-1]

        if law_complement != "":
            result = "%s %s" % (result[0], law_complement)

        else:
            result = result[0]

        if is_simple(result):
            return ms.SimpleLawRef(result)

        if is_multi(result):
            return ms.MultiLawRef(result)

        raise ms.ReferenceObjectException()

    except Exception:
        raise ms.ReferenceObjectException()


def get_right_from_ivm(s):
    try:
        result = re.split(r" [iI][.]?[Vv][.]?[mM][.]? ", s)[1]
        if is_simple(result):
            return ms.SimpleLawRef(result)

        if is_multi(result):
            return ms.MultiLawRef(result)

        raise ms.ReferenceObjectException()

    except Exception:
        raise ms.ReferenceObjectException()


def get_n_kammer_from_fileref(s):
    result = s.split(" ")
    if len(result) != 3:
        raise ms.ReferenceObjectException()

    if is_roman(result[0]):
        return roman_to_arabic(result[0])

    return result[0]


def get_kammer_from_fileref(s):
    result = s.split(" ")
    if len(result) != 3:
        raise ms.ReferenceObjectException()

    return result[1]


def get_nr_from_fileref(s):
    result = s.split(" ")
    if len(result) != 3:
        raise ms.ReferenceObjectException()

    if s.count("/") != 1:
        if s.count(".") != 1:
            raise ms.ReferenceObjectException()

        return result[2].split(".")[0]

    return result[2].split("/")[0]


def get_jahr_from_fileref(s):
    result = s.split(" ")
    if len(result) != 3:
        raise ms.ReferenceObjectException()

    if s.count("/") != 1:
        if s.count(".") != 1:
            raise ms.ReferenceObjectException()

        return result[2].split(".")[1]

    return result[2].split("/")[1]


def remove_html_absatzRechts(mn_split):
    return remove_html_common(mn_split)


def remove_html_rd(mn_split):
    return remove_html_common(mn_split)


def remove_html_nr(mn_split):
    mns = [0]
    for tag in mn_split[1::2]:
        mns.append(int(BeautifulSoup(tag, "html.parser").find("rd")["nr"]))

    mn_split = mn_split[::2]
    for i in range(len(mn_split)):
        mn_split[i] = BeautifulSoup(mn_split[i], "html.parser").get_text()

    return mn_split, mns


def remove_html_point(mn_split):
    return remove_html_common(mn_split)


def remove_html_none(content):
    return [BeautifulSoup(content, "html.parser").get_text()], [0]


def remove_html_common(mn_split):
    mns = [0]
    mn_split[0] = BeautifulSoup(mn_split[0], "html.parser").get_text()
    for i in range(1, len(mn_split)):
        find_lt = mn_split[i].find("<")
        mns.append(int(mn_split[i][:find_lt]))
        mn_split[i] = BeautifulSoup(mn_split[i][find_lt:], "html.parser").get_text()

    return mn_split, mns


def create_custom_simple(dic):
    try:
        keys, result = d.keys(), "§ %s" % dic["paragraph"]
        if "abs" in keys:
            result = "%s Abs. %s" % (result, dic["abs"])

        if "satz" in keys:
            result = "%s S. %s" % (result, dic["satz"])

        if "nr" in keys:
            result = "%s Nr. %s" % (result, dic["nr"])

        result = "%s %s" % (result, dic["vorschrift"])
        if "buch" in keys:
            result = "%s %s" % (result, dic["buch"])

        return ms.SimpleLawRef(result)

    except Exception:
        raise ms.ReferenceObjectException()
