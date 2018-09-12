
from bmeg.emitter import new_emitter
from bmeg.ioutils import reader
from bmeg.util.cli import default_argument_parser
from bmeg.util.logging import default_logging
from bmeg.vertex import Compound
from bmeg.edge import *
from bmeg.enrichers.drug_enricher import normalize
from bmeg.gid import GID

import glob
import logging
import sys
import ujson
import threading

threading.local().skip_check_types = True

def transform(
    prefix="compound",
    emitter_name="json",
    output_dir="outputs",
    vertex_names="**/*.Compound.Vertex.json",
    edge_names="**/*.*.Edge.json",
):
    batch_size = 100
    compound_cache = {}
    emitter = new_emitter(name=emitter_name, prefix=prefix)
    path = '{}/{}'.format(output_dir, vertex_names)
    files = [filename for filename in glob.iglob(path, recursive=True)]
    c = t = e = 0
    for file in files:
        logging.info(file)
        with reader(file) as ins:
            for line in ins:
                try:
                    compound = ujson.loads(line)
                    compound_gid = compound['gid']
                    compound = compound['data']
                    if compound['term'] == 'TODO':
                        ontology_terms = normalize(compound['name'])
                        if len(ontology_terms) == 0:
                            compound['term'] = compound['name']
                            compound['term_id'] = 'NO_ONTOLOGY~{}'.format(compound['term'])
                        else:
                            compound['term'] = ontology_terms[0]['synonym']
                            compound['term_id'] = ontology_terms[0]['ontology_term']
                    compound = Compound.from_dict(compound)
                    emitter.emit_vertex(compound)
                    compound_cache[compound_gid] = compound
                    c += 1 ; t += 1
                except Exception as exc:
                    logging.warning(str(exc))
                    raise
                    e += 1
                if c % batch_size == 0:
                    logging.info('transforming read: {} errors: {}'.format(t, e))
                    c = 0
        logging.info('transforming read: {} errors: {}'.format(t, e))

    path = '{}/{}'.format(output_dir, edge_names)
    files = [filename for filename in glob.iglob(path, recursive=True)]
    c = t = e = 0
    for file in files:
        logging.info(file)
        with reader(file) as ins:
            for line in ins:
                try:
                    edge = ujson.loads(line)
                    if 'Compound:TODO' not in edge['gid']:
                        logging.info('Edge {} has no compounds that need transformation. skipping.'.format(file))
                        break
                    # get edge components
                    label = edge['label']
                    from_ = edge['from']
                    to = edge['to']
                    data = edge['data']
                    # replace with normalized compound
                    if to in compound_cache:
                        to = compound_cache[to].gid()
                    if from_ in compound_cache:
                        from_ = compound_cache[from_].gid()
                    cls = globals()[label]
                    emitter.emit_edge(
                        cls(),
                        GID(from_),
                        GID(to),
                    )
                    c += 1 ; t += 1
                except Exception as exc:
                    logging.warning(str(exc))
                    raise
                    e += 1
                if c % batch_size == 0:
                    logging.info('transforming read: {} errors: {}'.format(t, e))
                    c = 0
        logging.info('transforming read: {} errors: {}'.format(t, e))


if __name__ == '__main__':  # pragma: no cover
    parser = default_argument_parser()
    options = parser.parse_args(sys.argv[1:])
    default_logging(options.loglevel)

    transform()
