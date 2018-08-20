

import json
import collections

from transform.g2p.genes import normalize as genes_normalize
from transform.g2p.features import normalize as features_normalize
from transform.g2p.environments import normalize as environments_normalize
from transform.g2p.phenotypes import normalize as phenotypes_normalize
from transform.g2p.association import normalize as association_normalize
from transform.g2p.publications import normalize as publication_normalize

import bmeg.ioutils
from bmeg.util.logging import default_logging
from bmeg.util.cli import default_argument_parser

from bmeg.edge import HasSupportingReference, GeneFeatureFor, AlleleFeatureFor, PhenotypeOf, EnvironmentFor
from bmeg.emitter import *  # noqa dynamic class instantiation

files = {}


def normalizeAssociations(path):
    """ create a record from input """
    input_stream = bmeg.ioutils.reader(path)
    # create a tuple where:
    # vertices - dict of vertices to be created
    # genes ... publications - arrays of edges from association
    NormalizedAssociation = collections.namedtuple(
        'NormalizedAssociation',
        ['vertices', 'genes', 'features', 'environments', 'phenotypes',
         'publications', 'association'])
    for line in input_stream:
        hit = json.loads(line)
        (hit, genes) = genes_normalize(hit)
        (hit, features) = features_normalize(hit)
        (hit, environments) = environments_normalize(hit)
        (hit, phenotypes) = phenotypes_normalize(hit)
        (hit, publications) = publication_normalize(hit)
        (hit, association) = association_normalize(hit)
        yield NormalizedAssociation(hit, genes, features, environments,
                                    phenotypes, publications, association)


def toGraph(normalized_association, emitter):
    """ tuple to graph edges and vertexes """
    na = normalized_association
    association = na.association
    emitter.emit_vertex(association)
    for publication in na.vertices['publications']:
        emitter.emit_vertex(publication)
    for publication_gid in na.publications:
        emitter.emit_edge(HasSupportingReference(),
                          association.gid(),
                          publication_gid
                          )
    # note we assume gene vertexes are already created
    for gene_gid in na.genes:
        emitter.emit_edge(GeneFeatureFor(),
                          association.gid(),
                          gene_gid
                          )
    for allele in na.vertices['features']:
        emitter.emit_vertex(allele)
    for feature_gid in na.features:
        emitter.emit_edge(AlleleFeatureFor(),
                          association.gid(),
                          feature_gid
                          )
    for phenotype in na.vertices['phenotypes']:
        emitter.emit_vertex(phenotype)
    for phenotype_gid in na.phenotypes:
        emitter.emit_edge(PhenotypeOf(),
                          association.gid(),
                          phenotype_gid
                          )
    for environment in na.vertices['environments']:
        emitter.emit_vertex(environment)
    for environment_gid in na.environments:
        emitter.emit_edge(EnvironmentFor(),
                          association.gid(),
                          environment_gid
                          )


def transform(input_path, prefix, emitter_class='JSONEmitter'):
    """ parse the association and write to graph using emitter"""
    klass = globals()[emitter_class]
    emitter = klass(prefix=prefix)

    for normalized_association in normalizeAssociations(input_path):
        toGraph(normalized_association, emitter)
    emitter.close()


def main():  # pragma: no cover
    parser = default_argument_parser()
    parser.add_argument('--input_path', type=str,
                        default='source/g2p/all.json.gz',
                        help='Path to g2p associations for import')
    parser.add_argument('--emitter', type=str,
                        default='JSONEmitter',
                        help='classname of emitter')

    # We don't need the first argument, which is the program name
    options = parser.parse_args()
    default_logging(options.loglevel)
    transform(options.input_path, prefix=options.prefix, emitter_class=options.emitter)


if __name__ == '__main__':
    main()
