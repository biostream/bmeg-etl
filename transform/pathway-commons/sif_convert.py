#!/usr/bin/env python

from __future__ import print_function

import argparse
import csv
import gzip
import json
import logging
import sys

from bmeg.vertex import Protein
from bmeg.edge import ProteinInteraction
from bmeg.emitter import JSONEmitter

def parse_gene_map(path):
    ensembl_cols = ["entrez_id", "ensembl_gene_id"]
    symbol_col = "symbol"
    prev_col = "prev_symbol"
    name_table = {}
    with open(path) as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        for row in reader:
            ensembl_id = None
            for ensembl_col in ensembl_cols:
                if len(row[ensembl_col]) > 0:
                    name_table[row[symbol_col]] = row[ensembl_col]
                    ensembl_id = row[ensembl_col]
            if ensembl_id and len(row[prev_col]) > 0:
                for ps in row[prev_col].split("|"):
                    name_table[ps] = row[ensembl_col]
    return name_table


def parse_sif(sif, name_table, emitter):
    with gzip.GzipFile(sif) as handle:
        for line in handle:
            row = line.decode().rstrip().split("\t")
            if not (row[0].startswith("CHEBI:") or row[2].startswith("CHEBI:")
                    or row[2].startswith("PubChem:")):

                if row[0] not in name_table:
                    logging.warning("%s not found" % (row[0]))
                elif row[2] not in name_table:
                    logging.warning("%s not found" % (row[2]))
                else:
                    pi = ProteinInteraction(interaction=row[1])
                    emitter.emit_edge(pi,
                        from_gid=name_table[row[0]],
                        to_gid=name_table[row[2]]
                    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser()
    # http://www.pathwaycommons.org/archives/PC2/v9/PathwayCommons9.All.hgnc.sif.gz
    parser.add_argument("-s", "--sif", required=True)
    # ftp://ftp.ebi.ac.uk/pub/databases/genenames/new/tsv/hgnc_complete_set.txt
    parser.add_argument("-g", "--gene-map", required=True)
    parser.add_argument("-o", "--output", default=sys.stdout)
    args = parser.parse_args()

    if args.output != sys.stdout:
        sys.stdout = open(args.output, 'w')

    name_table = parse_gene_map(args.gene_map)
    parse_sif(args.sif, name_table)
