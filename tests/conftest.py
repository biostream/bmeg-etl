import pytest
import os
import json
import gripql
import contextlib
import bmeg.ioutils


class Helpers:

    @staticmethod
    def assert_vertex_keys_populated(vertex_dict):
        """ ensure that graph keys populated """
        required = ['_id', 'gid', 'label', 'data']
        assert list(vertex_dict.keys()) == required, 'expected keys'
        for k in required:
            assert vertex_dict[k], 'empty key %s' % k
        if 'project_id' in vertex_dict['data'] and vertex_dict['label'] != "Project":
            assert vertex_dict['data']['project_id'].startswith("Project:"), 'expected data.project_id to be a Project GID'

    @staticmethod
    def assert_edge_keys_populated(edge_dict):
        """ ensure that graph keys populated """
        required = ['_id', 'gid', 'label', 'from', 'to', 'data']
        assert list(edge_dict.keys()) == required, 'expected keys'
        for k in required:
            if k == 'data':
                assert isinstance(edge_dict[k], dict)
                continue
            assert edge_dict[k], 'empty key %s' % k

    @staticmethod
    def assert_vertex_file_valid(vertex_file_path):
        """ ensure file exists; populated with json objs with required keys """
        assert os.path.isfile(vertex_file_path), vertex_file_path
        c = 0
        dups = {}
        with bmeg.ioutils.reader(vertex_file_path) as f:
            for line in f:
                # should be json
                vertex_dict = json.loads(line)
                # check expected keys
                Helpers.assert_vertex_keys_populated(vertex_dict)
                # no duplicates
                assert vertex_dict['gid'] not in dups
                dups[vertex_dict['gid']] = True
                c += 1
        return c

    @staticmethod
    def assert_edge_file_valid(edge_file_path):
        """ ensure file exists; populated with json objs with required keys """
        assert os.path.isfile(edge_file_path), edge_file_path
        c = 0
        dups = {}
        with bmeg.ioutils.reader(edge_file_path) as f:
            for line in f:
                # should be json
                edge_dict = json.loads(line)
                # check expected eys
                Helpers.assert_edge_keys_populated(edge_dict)
                # no duplicates
                assert edge_dict['gid'] not in dups
                dups[edge_dict['gid']] = True
                c += 1
        return c

    @staticmethod
    def parse_edge_file(edge_file_path):
        """ ensure file exists; return [edge] """
        assert os.path.isfile(edge_file_path)
        with bmeg.ioutils.reader(edge_file_path) as f:
            for line in f:
                # should be json
                yield json.loads(line)

    @staticmethod
    def load_stores(graph_file_paths):
        """ load an in memory 'graph' returns (vertices, edges)"""
        vertices = {}
        edges = {}
        for graph_file_path in graph_file_paths:
            with contextlib.suppress(FileNotFoundError):
                with bmeg.ioutils.reader(graph_file_path) as f:
                    store = vertices
                    if 'Edge' in graph_file_path:
                        store = edges
                    for line in f:
                        obj = json.loads(line)
                        store[obj['gid']] = obj
        return vertices, edges

    @staticmethod
    def assert_edge_has_vertex(vertices, edges, exclude_labels=[]):
        """ensure that all edges have vertexes"""
        for edge_gid in edges.keys():
            edge = edges[edge_gid]
            _from = edge['from']  # from keyword workaround
            label = _from.split(':')[0]
            if label in exclude_labels:
                continue
            elif any(x in exclude_labels for x in ["Gene", "Transcript", "Exon", "Protein"]):
                if label.startswith("ENS"):
                    continue
            _to = edge['to']
            label = _to.split(':')[0]
            if label in exclude_labels:
                continue
            elif any(x in exclude_labels for x in ["Gene", "Transcript", "Exon", "Protein"]):
                if label.startswith("ENS"):
                    continue
            assert vertices.get(_from, None), 'edge {} from {} does not exist'.format(edge_gid, _from)
            assert vertices.get(_to, None), 'edge {} from {} does not exist'.format(edge_gid, _to)

    @staticmethod
    def assert_vertex_has_edge(vertices, edges, exclude_labels=[]):
        """ensure that all vertexes have edge"""
        froms = [edges[gid]['from'] for gid in edges.keys()]
        tos = [edges[gid]['to'] for gid in edges.keys()]
        for vertex_gid in vertices.keys():
            label = vertex_gid.split(':')[0]
            if label in exclude_labels:
                continue
            if label == 'Deadletter':
                continue
            assert vertex_gid in froms or vertex_gid in tos, 'could not find {} in edge'.format(vertex_gid)

    @staticmethod
    def assert_edge_joins_valid(graph_file_paths, exclude_labels=[]):
        """ load an in memory 'graph', ensure all edges link to a vertex and vice versa"""
        vertices, edges = Helpers.load_stores(graph_file_paths)
        Helpers.assert_edge_has_vertex(vertices, edges, exclude_labels)
        Helpers.assert_vertex_has_edge(vertices, edges, exclude_labels)


@pytest.fixture
def helpers():
    """ ratify Helper class """
    return Helpers


@pytest.fixture(scope="module")
def graph():
    """ return a connection to the bmeg graph (control w/ BMEG_URL, BMEG_GRAPH, BMEG_CREDENTIAL_FILE env var) """
    bmeg_url = os.getenv('BMEG_URL', 'https://bmeg.io/api')
    bmeg_graph = os.getenv('BMEG_GRAPH', "bmeg_rc2")
    bmeg_credential_file = os.getenv('BMEG_CREDENTIAL_FILE', '/tmp/bmeg_credentials.json')
    return gripql.graph.Graph(url=bmeg_url, graph=bmeg_graph, credential_file=bmeg_credential_file)


@pytest.fixture(scope="module")
def V(graph):
    """ return the Vertex in the bmeg graph """
    return graph.query().V()


@pytest.fixture(scope="module")
def E(graph):
    """ return the Edge in the bmeg graph """
    return graph.query().E()


@pytest.fixture
def emitter_directory(request):
    """ get the full path of the test output """
    return os.path.join(request.fspath.dirname, 'test')


@pytest.fixture
def emitter_prefix(request):
    """ get the full path of the test output """
    return 'test'
