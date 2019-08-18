from transform.tcia.tcia_transformer import TCIATransformer
from collections import defaultdict


def test_transformer():
    G = TCIATransformer().graph()
    assert len(G.nodes) == 188666, 'Should have lots of nodes {}'.format(len(G.nodes))

    node_counts = defaultdict(int)
    for k, v in list(G.nodes.data()):
        node_counts[v['label']] += 1
    actual = sorted(node_counts.items())
    expected = [('Case', 18201), ('Demographic', 18201), ('Project', 88), ('Series', 121158), ('Study', 31018)]
    assert actual == expected, 'Should return expected node set'
