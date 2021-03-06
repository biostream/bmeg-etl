import pytest
import os
import contextlib
import shutil

from transform.pfam.transform import transform


@pytest.fixture
def pfam_xmls(request):
    return os.path.join(request.fspath.dirname, 'source/pfam/*.xml')


@pytest.fixture
def clans_file(request):
    return os.path.join(request.fspath.dirname, 'source/pfam/clans.tsv')


def test_simple(helpers, emitter_directory, pfam_xmls, clans_file):
    pfam_clan_file = os.path.join(emitter_directory, "PfamClan.Vertex.json.gz")
    pfam_family_file = os.path.join(emitter_directory, "PfamFamily.Vertex.json.gz")

    clan_family_edge_file = os.path.join(emitter_directory, "PfamClan_PfamFamilies_PfamFamily.Edge.json.gz")
    family_clan_edge_file = os.path.join(emitter_directory, "PfamFamily_PfamClans_PfamClan.Edge.json.gz")
    go_family_edge_file = os.path.join(emitter_directory, "GeneOntologyTerm_PfamFamilies_PfamFamily.Edge.json.gz")
    family_go_edge_file = os.path.join(emitter_directory, "PfamFamily_GeneOntologyTerms_GeneOntologyTerm.Edge.json.gz")

    all_files = [
        pfam_clan_file, pfam_family_file,
        clan_family_edge_file, family_clan_edge_file,
        go_family_edge_file, family_go_edge_file
    ]

    # remove output
    with contextlib.suppress(FileNotFoundError):
        shutil.rmtree(emitter_directory)

    # run transform
    transform(pfam_xmls=pfam_xmls,
              clans_file=clans_file,
              emitter_prefix=None,
              emitter_directory=emitter_directory)

    # check results
    for f in all_files:
        if "Vertex.json.gz" in f:
            helpers.assert_vertex_file_valid(f)
        elif "Edge.json.gz" in f:
            helpers.assert_edge_file_valid(f)

    helpers.assert_edge_joins_valid(
        all_files,
        exclude_labels=["GeneOntologyTerm"]
    )
