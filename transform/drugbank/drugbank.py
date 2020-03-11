#!/usr/bin/env python

import sys
import json
import xmltodict
from zipfile import ZipFile


resourceCount = {}
def handle_record(_, rec):
    #print(json.dumps(rec))
    id = rec['drugbank-id']
    name = rec['name']

    pubchemID = None
    chemblID = None

    # Get common ID
    ids = rec["external-identifiers"]["external-identifier"]
    if isinstance(ids, str):
        ids = [ids]
    for i in ids:
        res = i["resource"]
        if res == "PubChem Compound":
            pubchemID = i["identifier"]
        if res == "ChEMBL":
            chemblID = i["identifier"]
    if pubchemID is not None:
        gid = "Compound:CID%s" % (pubchemID)
    elif chemblID is not None:
        gid = "Compound:%s" % (chemblID)
    else:
        gid =  "Compound:%s" % (name)

    # Get literature Refs
    papers = []
    if "articles" in rec["general-references"] and rec["general-references"]["articles"] is not None:
        if "article" in rec["general-references"]["articles"]:
            papers = rec["general-references"]["articles"]["article"]
    if not isinstance(papers, list):
        papers = [papers]

    refs = []
    for p in papers:
        refs.append("PMID:%s" %(p["pubmed-id"]))

    actions = []

    if "targets" in rec:
        targets = rec["targets"]["target"]
        if not isinstance(targets, list):
            targets = [targets]

        print(json.dumps())


    out = {
        "gid" : gid,
        "refs" : refs
    }
    #print(json.dumps(out))

    return True

with ZipFile(sys.argv[1]) as myzip:
    with myzip.open("full database.xml") as myfile:
        xmltodict.parse(myfile, item_depth=2, item_callback=handle_record)

print(resourceCount)
