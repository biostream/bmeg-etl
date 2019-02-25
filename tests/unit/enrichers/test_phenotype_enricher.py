import bmeg.enrichers.phenotype_enricher as phenotype_enricher
import logging
from pprint import pprint

# maintain fresh cache for all calls
from uncacher import uncache
uncache(phenotype_enricher.requests)


NAMES = """
BOCA
cancer
Hodgkin_lymphoma
transitional_cell_carcinoma
""".strip().split("\n")

EXPECTED = [
    [{'label': 'bone cancer', 'name': 'BOCA', 'ontology_term': 'MONDO:0002129', 'provenance': 'https://www.ebi.ac.uk/ols/api/search?q=Bone+Cancer&groupField=iri&exact=on&start=0&ontology=mondo', 'source': 'http://purl.obolibrary.org/obo/MONDO_0002129'}],
    [{'family': 'neoplasm (disease)', 'label': 'cancer', 'name': 'cancer', 'ontology_term': 'MONDO:0004992', 'provenance': 'https://www.ebi.ac.uk/ols/api/search?q=cancer&groupField=iri&exact=on&start=0&ontology=mondo', 'source': 'http://purl.obolibrary.org/obo/MONDO_0004992'}],
    [{'family': 'lymphoid neoplasm', 'label': 'lymphoma', 'name': 'Hodgkin_lymphoma', 'ontology_term': 'MONDO:0005062', 'provenance': 'https://www.ebi.ac.uk/ols/api/search?q=lymphoma&groupField=iri&exact=on&start=0&ontology=mondo', 'source': 'http://purl.obolibrary.org/obo/MONDO_0005062'}],
    [{'family': 'carcinoma', 'label': 'transitional cell carcinoma', 'name': 'transitional_cell_carcinoma', 'ontology_term': 'MONDO:0006474', 'provenance': 'https://www.ebi.ac.uk/ols/api/search?q=transitional+cell+carcinoma&groupField=iri&exact=on&start=0&ontology=mondo', 'source': 'http://purl.obolibrary.org/obo/MONDO_0006474'}, {'family': 'cancer', 'label': 'carcinoma', 'name': 'transitional_cell_carcinoma', 'ontology_term': 'MONDO:0004993', 'provenance': 'https://www.ebi.ac.uk/ols/api/search?q=carcinoma&groupField=iri&exact=on&start=0&ontology=mondo', 'source': 'http://purl.obolibrary.org/obo/MONDO_0004993'}],
]


def test_simple(caplog):
    """ straightforward """
    caplog.set_level(logging.DEBUG)
    for name, expected in zip(NAMES, EXPECTED):
        actual = phenotype_enricher.normalize(name)
        try:
            assert actual, 'Should return value for {}'.format(name)
            assert len(actual) == len(expected), 'Should return same number of hits for {}'.format(name)
            for i, val in enumerate(expected):
                for f in expected[i].keys():
                    assert f in actual[i], '{} not found in actual'.format(f)
                    assert actual[i][f] == expected[i][f], '{} mismatch'.format(f)
        except Exception as e:
            print(str(e))
            pprint(actual)
            pprint(expected)
            assert False, 'Failed'
