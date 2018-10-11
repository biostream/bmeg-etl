
import os
import contextlib
import pytest
import json
from transform.gdsc.response import transform, BROAD_LOOKUP
from bmeg.vertex import Compound, DrugResponse, Aliquot


@pytest.fixture
def GDSC_AUC_file(request):
    """ get the full path of the test fixture """
    return os.path.join(request.fspath.dirname, 'source/gdsc/GDSC_AUC.csv')


ALL_FILES = """
Compound.Vertex.json
DrugResponse.Vertex.json
DrugResponseIn.Edge.json
ResponseTo.Edge.json
""".strip().split()


def validate(helpers, GDSC_AUC_file, emitter_directory, emitter_prefix):

    all_files = ['{}/{}.{}'.format(emitter_directory, emitter_prefix, f) for f in ALL_FILES]
    # remove output
    with contextlib.suppress(FileNotFoundError):
        for f in all_files:
            os.remove(f)

    # create output
    transform(path=GDSC_AUC_file, emitter_directory=emitter_directory, emitter_prefix=emitter_prefix)

    compounds = all_files[0]
    drug_responses = all_files[1]
    drug_response_ins = all_files[2]
    response_tos = all_files[3]

    c = helpers.assert_vertex_file_valid(Compound, compounds)
    assert c == 9, 'Should have 9 compounds'
    helpers.assert_vertex_file_valid(DrugResponse, drug_responses)
    helpers.assert_edge_file_valid(DrugResponse, Aliquot, drug_response_ins)
    helpers.assert_edge_file_valid(DrugResponse, Compound, response_tos)

    # validate vertex for all edges exist
    helpers.assert_edge_joins_valid(all_files, exclude_labels=['Aliquot'])

    # test BioSample edges
    aliquot_ids = set()
    with open(drug_response_ins, 'r', encoding='utf-8') as f:
        for line in f:
            drug_response_in = json.loads(line)
            assert 'ACH-' in drug_response_in['to'], 'should use broad_ids'
            aliquot_ids.add(drug_response_in['to'])
    for k in BROAD_LOOKUP:
        assert 'Aliquot:{}'.format(BROAD_LOOKUP[k]) in aliquot_ids, 'should remap {} to {}'.format(k, BROAD_LOOKUP[k])


def test_simple(helpers, GDSC_AUC_file, emitter_directory, emitter_prefix):
    validate(helpers, GDSC_AUC_file, emitter_directory, emitter_prefix)


def test_BROAD_LOOKUP(helpers):
    assert BROAD_LOOKUP.get("EFM19_BREAST", "foo") == "ACH-000330", 'should return ACH-000330'
