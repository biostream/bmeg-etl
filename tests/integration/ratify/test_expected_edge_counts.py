
"""
a set of very basic queries - simply ensure the counts of label->label
"""

import time
from gripql import eq
import json
import logging

EXPECTED_COUNTS = [
    {'_from': 'Sample', 'to': 'Case', 'via': 'case', 'expected_count': 79239, 'expected_time': 20},
    {'_from': 'Case', 'to': 'Project', 'via': 'projects', 'expected_count': 37861, 'expected_time': 10},
    {'_from': 'Aliquot', 'to': 'Sample', 'via': 'sample', 'expected_count': 853494, 'expected_time': 200},
    {'_from': 'Protein', 'to': 'PfamFamily', 'via': 'pfam_families', 'expected_count': 87547, 'expected_time': 15},
    {'_from': 'Protein', 'to': 'Transcript', 'via': 'transcript', 'expected_count': 94446, 'expected_time': 60},
    # {'_from': 'Gene', 'to': 'Allele', 'via': 'alleles', 'expected_count': 94446, 'expected_time': 500},
]


class Stopwatch:

    # Construct self and start it running.
    def __init__(self):
        self.creationTime = time.time()  # Creation time

    # Return the elapsed time since creation of self, in seconds.
    def elapsedTime(self):
        return time.time() - self.creationTime


def count_traversal(_from, to, expected_count, V, via=None, expected_time=60):
    """ count traversal template query """
    watch = Stopwatch()
    if via:
        q = V.hasLabel(_from).out(via).hasLabel(to).count()
    else:
        q = V.hasLabel(_from).out().hasLabel(to).count()
    query_string = json.dumps(q.to_dict(), separators=(',', ':'))
    print(list(q))
    actual_count = list(q)[0]['count']
    actual_time = watch.elapsedTime()
    via_msg = via
    if not via_msg:
        via_msg = 'any'
    print('{} {}-{}->{} {}'.format(actual_time, _from, via_msg, to, actual_count))
    if actual_count != expected_count:
        return 'Expected from:{} to:{} expected:{} actual: {}\n    {}'.format(
            _from, to, expected_count, actual_count, query_string
        )
    if actual_time > expected_time:
        return 'Time exceeded from:{} to:{} expected:{} actual: {}\n    {}'.format(
            _from, to, expected_time, actual_time, query_string
        )


def test_expected_counts(V, caplog):
    """ iterate through EXPECTED_COUNTS, assert expected_count """
    caplog.set_level(logging.INFO)
    errors = []
    for traversal in EXPECTED_COUNTS:
        print(traversal)
        error_msg = count_traversal(**traversal, V=V)
        if error_msg:
            errors.append(error_msg)
    if len(errors) != 0:
        print(errors)
        assert False, 'Should have no errors'


def test_expected_exon_transcript(V, caplog):
    """ subset only for one chromosome """
    caplog.set_level(logging.INFO)
    q = (
        V
        .hasLabel('Gene')
        .has(eq("chromosome", '22'))
        .in_()
        .hasLabel('Transcript')
        .count()
    )
    actual_count = list(q)[0]['count']
    assert actual_count == 4459, 'Expected from:Gene, chromosome:22 to:Transcript expected:4423 actual: {}'.format(actual_count)


def test_expected_drug_response(V, caplog):
    """Tests count of samples with drugresponse."""
    caplog.set_level(logging.INFO)
    q = (
        V
        .hasLabel('DrugResponse')
        .out('ResponseIn')
        .hasLabel('Aliquot')
        .out('AliquotFor')
        .hasLabel('Sample')
        .count()
    )
    watch = Stopwatch()
    actual_count = list(q)[0]['count']
    actual_time = watch.elapsedTime()
    query_string = json.dumps(q.to_dict(), separators=(',', ':'))
    assert actual_count == 596490, 'Expected DrugResponse->Aliquot->Sample actual: {} q:{}'.format(actual_count, query_string)
    assert actual_time < 300, 'Expected DrugResponse->Aliquot->Sample < 300 sec actual: {} q:{}'.format(actual_time, query_string)


# never returns: {'_from': 'Allele', 'to': 'Callset', 'via': 'AlleleCall',  'expected_count': 1},

def test_expected_allele_callset(V, caplog):
    """ subset only for one chromosome """
    caplog.set_level(logging.INFO)
    q = (
        V.hasLabel('Gene')
        .hasId("ENSG00000141510")
        .in_('AlleleIn')
        .hasLabel('Allele')
        .in_('AlleleCall')
        .hasLabel('Callset')
        .count()
    )
    watch = Stopwatch()
    actual_count = list(q)[0]['count']
    actual_time = watch.elapsedTime()
    query_string = json.dumps(q.to_dict(), separators=(',', ':'))
    assert actual_count == 5879, 'Expected Gene->AlleleIn->Allele->Callset->AlleleCall actual: {} q:{}'.format(actual_count, query_string)
    assert actual_time < 7, 'Expected Gene->AlleleIn->Allele->Callset->AlleleCall < 7 sec actual: {} q:{}'.format(actual_time, query_string)


def test_expected_g2p_associations(V, caplog):
    """ subset only for one gene """
    caplog.set_level(logging.INFO)
    q = (
        V.hasLabel("Gene").has(eq("$.symbol", "BRCA1")).in_("HasGeneFeature")
        .count()
    )
    watch = Stopwatch()
    actual_count = list(q)[0]['count']
    actual_time = watch.elapsedTime()
    query_string = json.dumps(q.to_dict(), separators=(',', ':'))
    assert actual_count > 1, 'Expected Gene->HasGeneFeature->G2PAssociation should be more than 1 actual: {} q:{}'.format(actual_count, query_string)
    assert actual_time < 7, 'Expected Gene->HasGeneFeature->G2PAssociation  < 7 sec actual: {} q:{}'.format(actual_time, query_string)
