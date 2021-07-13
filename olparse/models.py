import json
import olparse.functions as fs


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
        self.slug = _json["slug"]
        self.content, self.margin_numbers = fs.remove_html(_json["content"])
        self.simples = fs.parse_simples(self.content)
        self.multis = fs.parse_multis(self.content)
        self.ivms = fs.parse_ivms(self.content)
        self.files = fs.parse_files(self.content)
