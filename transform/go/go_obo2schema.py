#!/usr/bin/env python

import re
import sys
import json
from bmeg import phenotype_pb2
from google.protobuf import json_format

re_section = re.compile(r'^\[(.*)\]')
re_field = re.compile(r'^(\w+): (.*)$')

def obo_parse(handle):

    rec = None
    for line in handle:
        res = re_section.search(line)
        if res:
            if rec is not None:
                yield rec
            rec = None
            if res.group(1) == "Term":
                rec = {"type":res.group(1)}
        else:
            if rec is not None:
                res = re_field.search(line)
                if res:
                    key = res.group(1)
                    val = res.group(2)
                    val = val.split(" ! ")[0]
                    if key in rec:
                        rec[key].append(val)
                    else:
                        rec[key] = [val]

    if rec is not None:
        yield rec

def unquote(s):
    res = re.search(r'"(.*)"', s)
    if res:
        return res.group(1)
    return s

def message_to_json(message):
    msg = json_format.MessageToDict(message, preserving_proto_field_name=True)
    return json.dumps(msg)

if __name__ == "__main__":

    with open(sys.argv[1]) as handle:
        for rec in obo_parse(handle):
            go = phenotype_pb2.GeneOntologyTerm()
            go.id = rec['id'][0]
            go.name = rec['name'][0]
            go.namespace = rec['namespace'][0]
            go.definition = unquote(rec['def'][0])
            if 'synonym' in rec:
                for i in rec['synonym']:
                    go.synonym.append(unquote(i))
            if 'is_a' in rec:
                for i in rec['is_a']:
                    go.is_a.append(i)
            if 'xref' in rec:
                for i in rec['xref']:
                    go.xref.append(i.split(" ")[0])
            print message_to_json(go)