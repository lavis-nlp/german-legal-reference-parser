# dict_keys(['id', 'code', 'slug', 'title', 'revision_date', 'latest', 'order'])

import sys
import json

jsonl = open("law_books.jsonl", "r")

try:
    law = json.loads(jsonl.readline())
except json.decoder.JSONDecodeError:
    exit()

while True:
    if sys.argv[1] in law["code"]:
        print("->", law["title"].strip())
    try:
        law = json.loads(jsonl.readline())
    except json.decoder.JSONDecodeError:
        exit()
