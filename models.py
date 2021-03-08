import json
import re
import functions as fs


LAWS_SET = set()
try:
    LAWS_SET.update([x.strip() for x in open("laws.txt", "r").readlines()])

except Exception:
    print("laws.txt file is missing")
    exit()

LAWS_STRING = "|".join(LAWS_SET)
P_absatzRechts = re.compile("<span [^>]*class=\"absatzRechts\">")
P_rd = re.compile("<a [^>]*name=\"rd_[\d]+\">")
P_nr = re.compile("(<rd [^>]*nr=\"[\d]+\"/>)")
P_point = re.compile("<p [^>]*id=\"point[\d]+\">")
P_simple = re.compile("( § | Art[.] | Artikel ).*(?! [iI][.]?[Vv][.]?[mM][.]? ).*((\d|\w)+/)*(%s|\b\w*[Gg]esetz\w*\b)(/(\d|\w)+)*( [IVXLCDM]*)?" % LAWS_STRING)
P_multi = re.compile("( §§ ).*(?! [iI][.]?[Vv][.]?[mM][.]? ).*((\d|\w)+/)*(%s|\b\w*[Gg]esetz\w*\b)(/(\d|\w)+)*( [IVXLCDM]*)?" % LAWS_STRING)
P_ivm = re.compile("( § | Art[.] | Artikel | §§ ).*( [iI][.]?[Vv][.]?[mM][.]? ).*((\d|\w)+/)*(%s|\b\w*[Gg]esetz\w*\b)(/(\d|\w)+)*( [IVXLCDM]*)?" % LAWS_STRING)
P_file = re.compile(r"-? (\d+|[IVXLCDM]+) \w+ \d+[/.]\d+ -?")


class ReferenceObjectException(Exception):
    pass


class ReferenceObject:
    pass


class LawRef(ReferenceObject):
    pass


class SimpleLawRef(LawRef):
    def __init__(self, refstring):
        self.vorschrift = fs.get_vorschrift_from_simple(refstring)
        self.buch = fs.get_buch_from_simple(refstring)
        self.paragraph = fs.get_paragraph_from_simple(refstring)
        self.abs = fs.get_abs_from_simple(refstring)
        self.satz = fs.get_satz_from_simple(refstring)
        self.nr = fs.get_nr_from_simple(refstring)

    def __hash__(self):
        return hash(self.vorschrift + self.buch + self.paragraph + self.abs + self.satz + self.nr)

    def __eq__(self, other):
        if type(other) != SimpleLawRef:
            return False

        return hash(self) == hash(other)

    def __str__(self):
        result = "§ %s" % self.paragraph
        if self.abs != "":
            result += " Abs. %s" % self.abs

        if self.satz != "":
            result += " S. %s" % self.satz

        if self.nr != "":
            result += " Nr. %s" % self.nr

        if self.buch != "":
            return result + " %s %s" % (self.vorschrift, self.buch)

        return result + " %s" % self.vorschrift


class MultiLawRef(LawRef):
    def __init__(self, refstring):
        self.lawrefs = fs.get_lawrefs_from_multi(refstring)

    def __hash__(self):
        return sum([hash(x) for x in self.lawrefs])

    def __eq__(self, other):
        if type(other) != MultiLawRef:
            return False

        return hash(self) == hash(other)

    def __str__(self):
        return "§§ %s %s" % (", ".join([" ".join(str(x)[2:].split(" ")[:-1]) for x in self.lawrefs]), str(self.lawrefs[0]).split(" ")[-1])


class IVMLawRef(LawRef):
    def __init__(self, refstring):
        self.left = fs.get_left_from_ivm(refstring)
        self.right = fs.get_right_from_ivm(refstring)

    def __hash__(self):
        return sum([hash(self.left), hash(self.right)])

    def __eq__(self, other):
        if type(other) != IVMLawRef:
            return False

        return hash(self) == hash(other)

    def __str__(self):
        return "%s i.V.m %s" % (str(self.left), str(self.right))


class FileRef(ReferenceObject):
    def __init__(self, refstring):
        self.n_kammer = fs.get_n_kammer_from_fileref(refstring)
        self.kammer = fs.get_kammer_from_fileref(refstring)
        self.nr = fs.get_nr_from_fileref(refstring)
        self.jahr = fs.get_jahr_from_fileref(refstring)

    def __hash__(self):
        return hash(str(self.n_kammer) + self.kammer + str(self.nr) + str(self.jahr))

    def __eq__(self, other):
        if type(other) != FileRef:
            return False

        return hash(self) == hash(other)

    def __str__(self):
        return "- %s %s %s/%s -" % (self.n_kammer, self.kammer, self.nr, self.jahr)


class Verdict:
    def __init__(self, jsonstring):
        _json = json.loads(jsonstring)
        self.id = _json["id"]
        self.slug = _json["slug"]
        self.court = _json["court"]
        self.file_number = _json["file_number"]
        self.date = _json["date"]
        self.created_date = _json["created_date"]
        self.updated_date = _json["updated_date"]
        self.type = _json["type"]
        self.ecli = _json["ecli"]
        self.content = self.remove_html(_json["content"])
        self.simples = self.parse_simples(self.content)
        self.multis = self.parse_multis(self.content)
        self.ivms = self.parse_ivms(self.content)
        self.files = self.parse_files(self.content)

    def remove_html(self, content):
        if P_absatzRechts.search(content):
            mn_split, mns = fs.remove_html_absatzRechts(P_absatzRechts.split(content))

        elif P_rd.search(content):
            mn_split, mns = fs.remove_html_rd(P_rd.split(content))

        elif P_nr.search(content):
            mn_split, mns = fs.remove_html_nr(P_nr.split(content))

        elif P_point.search(content):
            mn_split, mns = fs.remove_html_point(P_point.split(content))

        else:
            mn_split, mns = fs.remove_html_none(content)

        offset = 0
        self.margin_numbers = dict()
        for i in range(len(mn_split)):
            self.margin_numbers[mns[i]] = offset
            offset += len(mn_split[i])

        return "".join(mn_split)

    def parse_simples(self, content):
        result = list()
        for x in P_simple.finditer(content):
            try:
                result.append((SimpleLawRef(x.group()), x.start()))

            except ReferenceObjectException:
                continue

        return result

    def parse_multis(self, content):
        result = list()
        for x in P_multi.finditer(content):
            try:
                result.append((MultiLawRef(x.group()), x.start()))

            except ReferenceObjectException:
                continue

        return result

    def parse_ivms(self, content):
        result = list()
        for x in P_ivm.finditer(content):
            try:
                result.append((IVMLawRef(x.group()), x.start()))

            except ReferenceObjectException:
                continue

        return result

    def parse_files(self, content):
        result = list()
        for x in P_file.finditer(content):
            try:
                result.append((FileRef(x.group()), x.start()))

            except ReferenceObjectException:
                continue

        return result
