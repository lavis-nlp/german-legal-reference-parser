# OpenLegalDataParser

This repository contains a library of python functions and classes with which
you can parse law book and file references from documents of the OpenLegalData
dataset and extract them into python objects. The implementation is incredibly
efficient. You can parse the whole OpenLegalData dataset within less than 200
minutes on modern machines. This README shall demonstrate how powerful this
library is:

## Definitions

First we will introduce some terminology that will be used throughout this
README:

* **simple** LawRef - a single reference to a law book, e.g. "§ 811 Abs. 1 Nr.
11 ZPO"
* **multi** LawRef - a reference to multiple sections of a law book, e.g. "§§ 3,
4 Nr. 3a) UWG"
* **IVM** LawRef - a combination ("in Verbindung mit") of references to law
books, e.g. "§ 291 S. 1 i.V.m § 288 Abs. 1 S. 2 BGB"
* **file** Ref - a reference to a file, e.g. "7 L 3645/97"

## Classes

models.py implements classes for the above defined reference types as well as
a class for a verdict which serves as a container for all references in that
verdict. This listing is not exhaustive of all classes.

### class SimpleLawRef

**Attributes**
* paragraph - the "Paragraph"
* abs - the "Absatz"
* satz - the "Satz"
* nr - the "Nummer"
* vorschrift - the "Vorschrift"
* buch - the "Buch"

**Methods**

This class implements \_\_hash\_\_, \_\_eq\_\_ and \_\_str\_\_.

To create an object call SimpleLawRef(x), where x is any simple LawRef string.

---

### class MultiLawRef

**Attributes**
* lawrefs - a python list of SimpleLawRef objects

**Methods**

This class implements \_\_hash\_\_, \_\_eq\_\_ and \_\_str\_\_.

To create an object call MultiLawRef(x), where x is any multi LawRef string.

---

### class IVMLawRef

**Attributes**
* left - the reference before "i.V.m."
* right - the reference after "i.V.m."

**Methods**

This class implements \_\_hash\_\_, \_\_eq\_\_ and \_\_str\_\_.

To create an object call IVMLawRef(x), where x is any IVM LawRef string.

---

### class FileRef

**Attributes**
* n_kammer - number of the "Kammer"
* kammer - the "Kammer"
* nr - the "Nummer"
* jahr - the "Jahr"

**Methods**

This class implements \_\_hash\_\_, \_\_eq\_\_ and \_\_str\_\_.

To create an object call FileRef(x), where x is any file Ref string.

---

### class Verdict

**Attributes**
* slug - the slug of this verdict
* content - the raw text of this verdict (without HTML and margin numbers)
* margin_numbers - a python dictionary where the keys are the margin numbers
and the values are the index within self.content where the margin number would
be
* simples - a python list of 2-tuples t where t[0] is a SimpleLawRef object and
t[1] is the index within self.content where the simple LawRef starts
* multis - a python list of 2-tuples t where t[0] is a MultiLawRef object and
t[1] is the index within self.content where the multi LawRef starts
* ivms - a python list of 2-tuples t where t[0] is a IVMLawRef object and t[1]
is the index within self.content where the IVM LawRef starts
* files - a python list of 2-tuples t where t[0] is a FileRef object and t[1] is
the index within self.content where the file Ref starts

To create an object call Verdict(x), where x is a jsonstring of a verdict from
the OpenLegalData dataset.

---

### class ReferenceObjectException

This class is a custom exception which is raised in case of parsing errors to
mask underlying errors like IndexError or TypeError.

---

The constructors of these classes call functions which are defined in functions.py.
The Ref objects hold the information of the reference in a sort of normalised
fashion. What we mean by this is that

```
SimpleLawRef("§ 19 Abs. 4 S. 1 BVerfGG") == SimpleLawRef("§ 19 IV 1 BVerfGG") == SimpleLawRef("§ 19 (4) 1 BVerfGG")
```

and even more complex comparisons like

```
IVMLawRef("§ 1 Abs. 4 Spiegelstrich 12 iVm § 2 (5) 3 ZPO") == IVMLawRef("Art. 1 IV lit. 12 IVM § II Absatz 5 Satz 3 ZPO")
```

evaluate to True.
This normalisation is done for simple, multi and IVM LawRefs and is very
powerful and useful for comparison and machine learning.

## Functions

functions.py implements the core functionality of this library. Some of the
functions serve as helper functions and are not very useful as standalones.
This listing is not exhaustive of all functions.

### get_X_from_simple

X is either paragraph, abs, satz, nr, vorschrift or buch.

These functions receive a string as input and return the respective information
in regard to X.

In case of the information not being found within the input string, an empty
string is returned instead, unless X is paragraph or vorschrift, then a
ReferenceObjectException is raised instead.

---

### get_lawrefs_from_multi

This function receives a string as input and returns a python list of
SimpleLawRef objects that correspond to the input string.

A ReferenceObjectException is raised if unsuccessful.

---

### get_X_from_IVM

X is either left or right.

These functions receive a string as input and return a LawRef object that
corresponds to the reference you would get if you were to split the input
string at "i.V.m." and, with respect to X, parse the result.

A ReferenceObjectException is raised if unsuccessful.

---

### get_X_from_file

X is either n_kammer, kammer, nr or jahr.

These functions receive a string as input and return the respective information
in regards to X.

A ReferenceObjectException is raised if unsuccessful.

---

### remove_html

The input to this function is a string of the kind you would get if you take a
sample of the OpenLegalData dataset and then select sample["content"].

This function returns two things. The first being the string from
sample["content"] without any HTML or margin numbers (raw text of the verdict)
and the second being a python dictionary where the keys are the margin
numbers and the values are the indeces within the raw text of the verdict where
the margin number would be.

In case of failure it instead returns a string with an error message and an
empty python dictionary.

---

### parse_X

X is either simples, multis, ivms or files.

The input for these functions is any string. The input string will be matched
against regular expressions to extract Refs with respect to X.

The functions return a python list of 2-tuples t where t[0] is a Ref object and
t[1] is the index within the input string where the Ref starts.

---

### create_custom_simple

The input for this function is a python dictionary with keys that correspond
to attributes from the SimpleLawRef class. You can omit any key except for
"paragraph" and "vorschrift".

The function returns a SimpleLawRef object with attribute values equal to the
values of the input dictionary at the corresponding key.

Example:

```
dic = dict()
dic["paragraph"] = "811"
dic["abs"] = "1"
dic["nr"] = "11"
dic["vorschrift"] = "ZPO"

create_custom_simple(dic) == SimpleLawRef("§ 811 Abs. 1 Nr. 11 ZPO")
```

evaluates to True.

A ReferenceObjectException is raised if unsuccessful.

## laws.txt

This file is a container where each line represents a law. The laws in this file
are used in regular expressions for parsing functions in functions.py. If the
parser does not recognise a particular law then you can add a line to this file
with the name of the law.

**IMPORTANT**: in rare cases names of laws overlap, e.g. SG, SGG and SGB all
start with "SG". For the parser to work correctly in these cases you need to
use regular expression syntax in the line you are adding to the file. So in this
case you would add "SG[GB]?" instead of adding three lines with SG, SGG and SGB.
If you want to add a year to the law then you have to do it in regular
expression syntax as well. This means instead of adding "SchSV 1998" you have to
add "SchSV( 1998)?".

## Example

As an example let us say that we want a programm that prints simple, multi, ivm
and file references from OpenLegalData samples as well as their corresponding
margin numbers and the slug of the verdict onto the terminal. The slug is useful
because it can be used in OpenLegalData URLs, e.g.
"de.openlegaldata.io/case/**slug**" takes you directly to the verdict.

Suppose we downloaded the OpenLegalData dataset from
https://static.openlegaldata.io/dumps/de/2020-12-10/, unzipped it and named the
file "cases.jsonl", then the following code would be sufficient to get what we
wanted:

```
import models as ms


def find_margin(value, dic):
    result = -1
    for key in dic.keys():
        if dic[key] <= value:
            result = key

        else:
            break

    return result


class Parser:
    def __init__(self, infile):
        self.infile = infile
        self.next_verdict()

    def next_verdict(self):
        self.verdict = ms.Verdict(self.infile.readline())


parser = Parser(open("cases.jsonl", "r"))
while True:
    print("\n\n\nSIMPLES")
    for x in parser.verdict.simples:
        print(str(x[0]), find_margin(x[1], parser.verdict.margin_numbers))

    print("\n\n\nMULTIS")
    for x in parser.verdict.multis:
        print(str(x[0]), find_margin(x[1], parser.verdict.margin_numbers))

    print("\n\n\nIVMS")
    for x in parser.verdict.ivms:
        print(str(x[0]), find_margin(x[1], parser.verdict.margin_numbers))

    print("\n\n\nFILES")
    for x in parser.verdict.files:
        print(str(x[0]), find_margin(x[1], parser.verdict.margin_numbers))

    print("\n\n\n" + parser.verdict.slug + "\n\n\n----------------------------")
    input()
    try:
        parser.next_verdict()

    except Exception:
        break

print("EOF")
```

Running this would parse one sample at a time (parse next sample by pressing
ENTER) and produce an output like the output below:

```
...
----------------------------




SIMPLES
§ 113 Abs. 5 S. 1 VwGO 24
§ 34 Beamtenversorgungsgesetz 25
§ 34 Abs. 1 S. 1 NBeamtVG 26
§ 51 NBeamtVG 32
§ 51 Abs. 1 NBeamtVG 33
§ 51 Abs. 1 NBeamtVG 33
§ 104 Abs. 3 S. 2 VwGO 36
§ 87b Abs. 3 VwGO 36



MULTIS



IVMS



FILES
- 2 A 6/18 - 25
- 5 LA 152/17 - 25
- 2 C 22/01 - 26
- 5 LA 155/07 - 26
- 2 L 3542/00 - 26
- 2 C 18/17 - 33



vg-gottingen-2020-12-02-3-a-24718


----------------------------
...
```

In the output each line is a reference from the verdict followed by under which
margin number the reference can be found. This can easily be verified by opening
"de.openlegaldata.io/case/vg-gottingen-2020-12-02-3-a-24718" in a browser.

There are countless ways to use the functionality that this library provides.

The simplicity of the example code shows the power of this library.

## Authors

Pitambara Kevin Pech - programming, testing, dataset analysis, documentation

Marco Wrzalik - concept and idea
