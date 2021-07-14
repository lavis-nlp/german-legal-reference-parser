from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Tuple, Union, List
from dataclasses import dataclass
from functools import lru_cache
import json
import olparse.functions as fs


class ReferenceException(Exception):
    pass


class Reference(ABC):
    @abstractmethod
    def unpack(self) -> List[Reference]:
        pass


class LawRef(Reference, ABC):
    pass

@dataclass(frozen=True)
class SimpleLawRef(LawRef):
    vorschrift: str
    buch: str
    paragraph: str
    abs: str
    satz: str
    nr: str

    @classmethod
    @lru_cache(maxsize=100000)
    def from_refstring(cls, refstring):
        return cls(
            vorschrift=fs.get_vorschrift_from_simple(refstring),
            buch=fs.get_buch_from_simple(refstring),
            paragraph=fs.get_paragraph_from_simple(refstring),
            abs=fs.get_abs_from_simple(refstring),
            satz=fs.get_satz_from_simple(refstring),
            nr=fs.get_nr_from_simple(refstring),
        )

    def unpack(self) -> List[SimpleLawRef]:
        return [self]

    # def __hash__(self):
    #     return hash(self.vorschrift + self.buch + self.paragraph + self.abs + self.satz + self.nr)

    # def __eq__(self, other):
    #     if type(other) != SimpleLawRef:
    #         return False
    #
    #     return hash(self) == hash(other)

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

    # def __repr__(self):
    #     return f"SimpleLawRef('{self.__str__()}')"


@dataclass(frozen=True)
class MultiLawRef(LawRef):
    lawrefs: Tuple[SimpleLawRef]

    @classmethod
    def from_refstring(cls, refstring):
        return cls(tuple(fs.get_lawrefs_from_multi(refstring)))

    def unpack(self) -> List[SimpleLawRef]:
        return list(self.lawrefs)

    # def __hash__(self):
    #     return sum([hash(x) for x in self.lawrefs])
    #
    # def __eq__(self, other):
    #     if type(other) != MultiLawRef:
    #         return False
    #
    #     return hash(self) == hash(other)

    def __str__(self):
        return "§§ %s %s" % (
            ", ".join([" ".join(str(x)[2:].split(" ")[:-1]) for x in self.lawrefs]),
            str(self.lawrefs[0]).split(" ")[-1],
        )


@dataclass(frozen=True)
class IVMLawRef(LawRef):
    left: Union[SimpleLawRef, MultiLawRef]
    right: Union[SimpleLawRef, MultiLawRef]

    @classmethod
    def from_refstring(cls, refstring):
        return cls(
            left=fs.get_left_from_ivm(refstring), right=fs.get_right_from_ivm(refstring)
        )

    def unpack(self) -> List[SimpleLawRef]:
        return self.left.unpack() + self.right.unpack()

    # def __hash__(self):
    #     return sum([hash(self.left), hash(self.right)])
    #
    # def __eq__(self, other):
    #     if type(other) != IVMLawRef:
    #         return False
    #
    #     return hash(self) == hash(other)

    def __str__(self):
        return "%s i.V.m %s" % (str(self.left), str(self.right))


@dataclass(frozen=True)
class FileRef(Reference):
    n_kammer: str
    kammer: str
    nr: str
    jahr: str

    @classmethod
    @lru_cache(maxsize=100000)
    def from_refstring(cls, refstring):
        return cls(
            n_kammer=fs.get_n_kammer_from_fileref(refstring),
            kammer=fs.get_kammer_from_fileref(refstring),
            nr=fs.get_nr_from_fileref(refstring),
            jahr=fs.get_jahr_from_fileref(refstring),
        )

    def unpack(self) -> List[FileRef]:
        return [self]

    # def __hash__(self):
    #     return hash(str(self.n_kammer) + self.kammer + str(self.nr) + str(self.jahr))
    #
    # def __eq__(self, other):
    #     if type(other) != FileRef:
    #         return False
    #
    #     return hash(self) == hash(other)

    def __str__(self):
        return "%s %s %s/%s" % (self.n_kammer, self.kammer, self.nr, self.jahr)

@dataclass()
class Verdict:
    slug:str
    content:str
    margin_numbers:str
    simples:List
    multis:List
    ivms:List
    files:List

    @classmethod
    def from_jsonstring(cls, jsonstring):
        _json = json.loads(jsonstring)
        content, margin_numbers = fs.remove_html(_json["content"])
        return cls(
            slug = _json["slug"],
            content=content,
            margin_numbers=margin_numbers,
            simples = fs.parse_simples(content),
            multis = fs.parse_multis(content),
            ivms = fs.parse_ivms(content),
            files = fs.parse_files(content),
        )
