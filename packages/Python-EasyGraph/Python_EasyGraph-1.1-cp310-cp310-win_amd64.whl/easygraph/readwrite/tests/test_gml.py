import codecs
import io
import os
import tempfile

from ast import literal_eval
from contextlib import contextmanager
from textwrap import dedent

import easygraph as eg
import pytest

from easygraph.readwrite.gml import literal_destringizer
from easygraph.readwrite.gml import literal_stringizer


class TestGraph:
    @classmethod
    def setup_class(cls):
        cls.simple_data = """Creator "me"
Version "xx"
graph [
 comment "This is a sample graph"
 directed 1
 IsPlanar 1
 pos  [ x 0 y 1 ]
 node [
   id 1
   label "Node 1"
   pos [ x 1 y 1 ]
 ]
 node [
    id 2
    pos [ x 1 y 2 ]
    label "Node 2"
    ]
  node [
    id 3
    label "Node 3"
    pos [ x 1 y 3 ]
  ]
  edge [
    source 1
    target 2
    label "Edge from node 1 to node 2"
    color [line "blue" thickness 3]

  ]
  edge [
    source 2
    target 3
    label "Edge from node 2 to node 3"
  ]
  edge [
    source 3
    target 1
    label "Edge from node 3 to node 1"
  ]
]
"""

    def test_parse_gml_cytoscape_bug(self):
        # example from issue #321, originally #324 in trac
        cytoscape_example = """
Creator "Cytoscape"
Version 1.0
graph   [
    node    [
        root_index  -3
        id  -3
        graphics    [
            x   -96.0
            y   -67.0
            w   40.0
            h   40.0
            fill    "#ff9999"
            type    "ellipse"
            outline "#666666"
            outline_width   1.5
        ]
        label   "node2"
    ]
    node    [
        root_index  -2
        id  -2
        graphics    [
            x   63.0
            y   37.0
            w   40.0
            h   40.0
            fill    "#ff9999"
            type    "ellipse"
            outline "#666666"
            outline_width   1.5
        ]
        label   "node1"
    ]
    node    [
        root_index  -1
        id  -1
        graphics    [
            x   -31.0
            y   -17.0
            w   40.0
            h   40.0
            fill    "#ff9999"
            type    "ellipse"
            outline "#666666"
            outline_width   1.5
        ]
        label   "node0"
    ]
    edge    [
        root_index  -2
        target  -2
        source  -1
        graphics    [
            width   1.5
            fill    "#0000ff"
            type    "line"
            Line    [
            ]
            source_arrow    0
            target_arrow    3
        ]
        label   "DirectedEdge"
    ]
    edge    [
        root_index  -1
        target  -1
        source  -3
        graphics    [
            width   1.5
            fill    "#0000ff"
            type    "line"
            Line    [
            ]
            source_arrow    0
            target_arrow    3
        ]
        label   "DirectedEdge"
    ]
]
"""
        eg.parse_gml(cytoscape_example)

    def test_parse_gml(self):
        G = eg.parse_gml(self.simple_data, label="label")
        assert sorted(G.nodes) == ["Node 1", "Node 2", "Node 3"]
        assert [e[:2] for e in sorted(G.edges)] == [
            ("Node 1", "Node 2"),
            ("Node 2", "Node 3"),
            ("Node 3", "Node 1"),
        ]

        assert [e for e in sorted(G.edges)] == [
            (
                "Node 1",
                "Node 2",
                {
                    "color": {"line": "blue", "thickness": 3},
                    "label": "Edge from node 1 to node 2",
                },
            ),
            ("Node 2", "Node 3", {"label": "Edge from node 2 to node 3"}),
            ("Node 3", "Node 1", {"label": "Edge from node 3 to node 1"}),
        ]

    def test_read_gml(self):
        (fd, fname) = tempfile.mkstemp()
        fh = open(fname, "w")
        fh.write(self.simple_data)
        fh.close()
        Gin = eg.read_gml(fname, label="label")
        G = eg.parse_gml(self.simple_data, label="label")
        assert sorted(G.nodes) == sorted(Gin.nodes)
        assert sorted(G.edges) == sorted(Gin.edges)
        os.close(fd)
        os.unlink(fname)

    def test_labels_are_strings(self):
        # GML requires labels to be strings (i.e., in quotes)
        answer = """graph [
  node [
    id 0
    label "1203"
  ]
]"""
        G = eg.Graph()
        G.add_node(1203)
        data = "\n".join(eg.generate_gml(G, stringizer=literal_stringizer))
        assert data == answer

    def test_relabel_duplicate(self):
        data = """
graph
[
        label   ""
        directed        1
        node
        [
                id      0
                label   "same"
        ]
        node
        [
                id      1
                label   "same"
        ]
]
"""
        fh = io.BytesIO(data.encode("UTF-8"))
        fh.seek(0)
        pytest.raises(eg.EasyGraphError, eg.read_gml, fh, label="label")

    def test_quotes(self):
        G = eg.path_graph(1)
        G.name = "path_graph(1)"
        attr = 'This is "quoted" and this is a copyright: ' + chr(169)
        G.nodes[0]["demo"] = attr
        fobj = tempfile.NamedTemporaryFile()
        eg.write_gml(G, fobj)
        fobj.seek(0)
        # Should be bytes in 2.x and 3.x
        data = fobj.read().strip().decode("ascii")
        answer = """graph [
  name "path_graph(1)"
  node [
    id 0
    label "0"
    demo "This is &#34;quoted&#34; and this is a copyright: &#169;"
  ]
]"""
        assert data == answer

    def test_unicode_node(self):
        node = "node" + chr(169)
        G = eg.Graph()
        G.add_node(node)
        fobj = tempfile.NamedTemporaryFile()
        eg.write_gml(G, fobj)
        fobj.seek(0)
        # Should be bytes in 2.x and 3.x
        data = fobj.read().strip().decode("ascii")
        answer = """graph [
  node [
    id 0
    label "node&#169;"
  ]
]"""
        assert data == answer

    def test_float_label(self):
        node = 1.0
        G = eg.Graph()
        G.add_node(node)
        fobj = tempfile.NamedTemporaryFile()
        eg.write_gml(G, fobj)
        fobj.seek(0)
        # Should be bytes in 2.x and 3.x
        data = fobj.read().strip().decode("ascii")
        answer = """graph [
  node [
    id 0
    label "1.0"
  ]
]"""
        assert data == answer

    def test_name(self):
        G = eg.parse_gml('graph [ name "x" node [ id 0 label "x" ] ]')
        assert "x" == G.graph["name"]
        G = eg.parse_gml('graph [ node [ id 0 label "x" ] ]')
        assert "" == G.name
        assert "name" not in G.graph

    def test_graph_types(self):
        for directed in [None, False, True]:
            for multigraph in [None, False, True]:
                gml = "graph ["
                if directed is not None:
                    gml += " directed " + str(int(directed))
                if multigraph is not None:
                    gml += " multigraph " + str(int(multigraph))
                gml += ' node [ id 0 label "0" ]'
                gml += " edge [ source 0 target 0 ]"
                gml += " ]"
                G = eg.parse_gml(gml)
                assert bool(directed) == G.is_directed()
                assert bool(multigraph) == G.is_multigraph()
                gml = "graph [\n"
                if directed is True:
                    gml += "  directed 1\n"
                if multigraph is True:
                    gml += "  multigraph 1\n"
                gml += """  node [
    id 0
    label "0"
  ]
  edge [
    source 0
    target 0
"""
                if multigraph:
                    gml += "    key 0\n"
                gml += "  ]\n]"
                assert gml == "\n".join(eg.generate_gml(G))

    def test_data_types(self):
        data = [
            True,
            False,
            10**20,
            -2e33,
            "'",
            '"&&amp;&&#34;"',
            [{(b"\xfd",): "\x7f", chr(0x4444): (1, 2)}, (2, "3")],
        ]
        data.append(chr(0x14444))
        data.append(literal_eval("{2.3j, 1 - 2.3j, ()}"))
        G = eg.Graph()
        G.name = data
        G.graph["data"] = data
        G.add_node(0, int=-1, data=dict(data=data))
        G.add_edge(0, 0, float=-2.5, data=data)
        gml = "\n".join(eg.generate_gml(G, stringizer=literal_stringizer))
        G = eg.parse_gml(gml, destringizer=literal_destringizer)
        assert data == G.name
        assert {"name": data, "data": data} == G.graph
        assert G.nodes == {0: dict(int=-1, data=dict(data=data))}
        assert list(G.edges) == [(0, 0, dict(float=-2.5, data=data))]
        G = eg.Graph()
        G.graph["data"] = "frozenset([1, 2, 3])"
        G = eg.parse_gml(eg.generate_gml(G), destringizer=literal_eval)
        assert G.graph["data"] == "frozenset([1, 2, 3])"

    def test_escape_unescape(self):
        gml = """graph [
  name "&amp;&#34;&#xf;&#x4444;&#1234567890;&#x1234567890abcdef;&unknown;"
]"""
        G = eg.parse_gml(gml)
        assert (
            '&"\x0f' + chr(0x4444) + "&#1234567890;&#x1234567890abcdef;&unknown;"
            == G.name
        )
        gml = "\n".join(eg.generate_gml(G))
        alnu = "#1234567890;&#38;#x1234567890abcdef"
        answer = (
            """graph [
  name "&#38;&#34;&#15;&#17476;&#38;"""
            + alnu
            + """;&#38;unknown;"
]"""
        )
        assert answer == gml

    def test_exceptions(self):
        pytest.raises(ValueError, literal_destringizer, "(")
        pytest.raises(ValueError, literal_destringizer, "frozenset([1, 2, 3])")
        pytest.raises(ValueError, literal_destringizer, literal_destringizer)
        pytest.raises(ValueError, literal_stringizer, frozenset([1, 2, 3]))
        pytest.raises(ValueError, literal_stringizer, literal_stringizer)
        with tempfile.TemporaryFile() as f:
            f.write(codecs.BOM_UTF8 + b"graph[]")
            f.seek(0)
            pytest.raises(eg.EasyGraphError, eg.read_gml, f)

        def assert_parse_error(gml):
            pytest.raises(eg.EasyGraphError, eg.parse_gml, gml)

        assert_parse_error(["graph [\n\n", "]"])
        assert_parse_error("")
        assert_parse_error('Creator ""')
        assert_parse_error("0")
        assert_parse_error("graph ]")
        assert_parse_error("graph [ 1 ]")
        assert_parse_error("graph [ 1.E+2 ]")
        assert_parse_error('graph [ "A" ]')
        assert_parse_error("graph [ ] graph ]")
        assert_parse_error("graph [ ] graph [ ]")
        assert_parse_error("graph [ data [1, 2, 3] ]")
        assert_parse_error("graph [ node [ ] ]")
        assert_parse_error("graph [ node [ id 0 ] ]")
        eg.parse_gml('graph [ node [ id "a" ] ]', label="id")
        assert_parse_error("graph [ node [ id 0 label 0 ] node [ id 0 label 1 ] ]")
        assert_parse_error("graph [ node [ id 0 label 0 ] node [ id 1 label 0 ] ]")
        assert_parse_error("graph [ node [ id 0 label 0 ] edge [ ] ]")
        assert_parse_error("graph [ node [ id 0 label 0 ] edge [ source 0 ] ]")
        eg.parse_gml("graph [edge [ source 0 target 0 ] node [ id 0 label 0 ] ]")
        assert_parse_error("graph [ node [ id 0 label 0 ] edge [ source 1 target 0 ] ]")
        assert_parse_error("graph [ node [ id 0 label 0 ] edge [ source 0 target 1 ] ]")
        assert_parse_error(
            "graph [ node [ id 0 label 0 ] node [ id 1 label 1 ] "
            "edge [ source 0 target 1 ] edge [ source 1 target 0 ] ]"
        )
        eg.parse_gml(
            "graph [ node [ id 0 label 0 ] node [ id 1 label 1 ] "
            "edge [ source 0 target 1 ] edge [ source 1 target 0 ] "
            "directed 1 ]"
        )
        eg.parse_gml(
            "graph [ node [ id 0 label 0 ] node [ id 1 label 1 ] "
            "edge [ source 0 target 1 ] edge [ source 0 target 1 ]"
            "multigraph 1 ]"
        )
        eg.parse_gml(
            "graph [ node [ id 0 label 0 ] node [ id 1 label 1 ] "
            "edge [ source 0 target 1 key 0 ] edge [ source 0 target 1 ]"
            "multigraph 1 ]"
        )
        assert_parse_error(
            "graph [ node [ id 0 label 0 ] node [ id 1 label 1 ] "
            "edge [ source 0 target 1 key 0 ] edge [ source 0 target 1 key 0 ]"
            "multigraph 1 ]"
        )
        eg.parse_gml(
            "graph [ node [ id 0 label 0 ] node [ id 1 label 1 ] "
            "edge [ source 0 target 1 key 0 ] edge [ source 1 target 0 key 0 ]"
            "directed 1 multigraph 1 ]"
        )

        # Tests for string convertible alphanumeric id and label values
        eg.parse_gml("graph [edge [ source a target a ] node [ id a label b ] ]")
        eg.parse_gml(
            "graph [ node [ id n42 label 0 ] node [ id x43 label 1 ]"
            "edge [ source n42 target x43 key 0 ]"
            "edge [ source x43 target n42 key 0 ]"
            "directed 1 multigraph 1 ]"
        )
        assert_parse_error(
            "graph [edge [ source u'u\4200' target u'u\4200' ] "
            + "node [ id u'u\4200' label b ] ]"
        )

        def assert_generate_error(*args, **kwargs):
            pytest.raises(
                eg.EasyGraphError, lambda: list(eg.generate_gml(*args, **kwargs))
            )

        G = eg.Graph()
        G.graph[3] = 3
        assert_generate_error(G)
        G = eg.Graph()
        G.graph["3"] = 3
        assert_generate_error(G)
        G = eg.Graph()
        G.graph["data"] = frozenset([1, 2, 3])
        assert_generate_error(G, stringizer=literal_stringizer)
        G = eg.Graph()
        G.graph["data"] = []
        assert_generate_error(G)
        assert_generate_error(G, stringizer=len)

    def test_label_kwarg(self):
        G = eg.parse_gml(self.simple_data, label="id")
        assert sorted(G.nodes) == [1, 2, 3]
        labels = [G.nodes[n]["label"] for n in sorted(G.nodes)]
        assert labels == ["Node 1", "Node 2", "Node 3"]

        G = eg.parse_gml(self.simple_data, label=None)
        assert sorted(G.nodes) == [1, 2, 3]
        labels = [G.nodes[n]["label"] for n in sorted(G.nodes)]
        assert labels == ["Node 1", "Node 2", "Node 3"]

    def test_outofrange_integers(self):
        # GML restricts integers to 32 signed bits.
        # Check that we honor this restriction on export
        G = eg.Graph()
        # Test export for numbers that barely fit or don't fit into 32 bits,
        # and 3 numbers in the middle
        numbers = {
            "toosmall": (-(2**31)) - 1,
            "small": -(2**31),
            "med1": -4,
            "med2": 0,
            "med3": 17,
            "big": (2**31) - 1,
            "toobig": 2**31,
        }
        G.add_node("Node", **numbers)

        fd, fname = tempfile.mkstemp()
        try:
            eg.write_gml(G, fname)
            # Check that the export wrote the nonfitting numbers as strings
            G2 = eg.read_gml(fname)
            for attr, value in G2.nodes["Node"].items():
                if attr == "toosmall" or attr == "toobig":
                    assert type(value) == str
                else:
                    assert type(value) == int
        finally:
            os.close(fd)
            os.unlink(fname)


@contextmanager
def byte_file():
    _file_handle = io.BytesIO()
    yield _file_handle
    _file_handle.seek(0)


class TestPropertyLists:
    def test_writing_graph_with_multi_element_property_list(self):
        g = eg.Graph()
        g.add_node("n1", properties=["element", 0, 1, 2.5, True, False])
        with byte_file() as f:
            eg.write_gml(g, f)
        result = f.read().decode()

        assert result == dedent(
            """\
            graph [
              node [
                id 0
                label "n1"
                properties "element"
                properties 0
                properties 1
                properties 2.5
                properties 1
                properties 0
              ]
            ]
        """
        )

    def test_writing_graph_with_one_element_property_list(self):
        g = eg.Graph()
        g.add_node("n1", properties=["element"])
        with byte_file() as f:
            eg.write_gml(g, f)
        result = f.read().decode()

        assert result == dedent(
            """\
            graph [
              node [
                id 0
                label "n1"
                properties "_easygraph_list_start"
                properties "element"
              ]
            ]
        """
        )

    def test_reading_graph_with_list_property(self):
        with byte_file() as f:
            f.write(
                dedent(
                    """
              graph [
                node [
                  id 0
                  label "n1"
                  properties "element"
                  properties 0
                  properties 1
                  properties 2.5
                ]
              ]
            """
                ).encode("ascii")
            )
            f.seek(0)
            graph = eg.read_gml(f)
        assert graph.nodes["n1"] == {"properties": ["element", 0, 1, 2.5]}

    def test_reading_graph_with_single_element_list_property(self):
        with byte_file() as f:
            f.write(
                dedent(
                    """
              graph [
                node [
                  id 0
                  label "n1"
                  properties "_easygraph_list_start"
                  properties "element"
                ]
              ]
            """
                ).encode("ascii")
            )
            f.seek(0)
            graph = eg.read_gml(f)
        assert graph.nodes["n1"] == {"properties": ["element"]}
