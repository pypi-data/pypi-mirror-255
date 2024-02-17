import easygraph as eg

from easygraph.utils import open_file


__all__ = [
    "parse_edgelist",
    "generate_edgelist",
    "write_edgelist",
    "read_edgelist",
    "read_weighted_edgelist",
    "write_weighted_edgelist",
]


def parse_edgelist(
    lines, comments="#", delimiter=None, create_using=None, nodetype=None, data=True
):
    """Parse lines of an edge list representation of a graph.

    Parameters
    ----------
    lines : list or iterator of strings
        Input data in edgelist format
    comments : string, optional
       Marker for comment lines. Default is `'#'`. To specify that no character
       should be treated as a comment, use ``comments=None``.
    delimiter : string, optional
       Separator for node labels. Default is `None`, meaning any whitespace.
    create_using : EasyGraph graph constructor, optional (default=eg.Graph)
       Graph type to create. If graph instance, then cleared before populated.
    nodetype : Python type, optional
       Convert nodes to this type. Default is `None`, meaning no conversion is
       performed.
    data : bool or list of (label,type) tuples
       If `False` generate no edge data or if `True` use a dictionary
       representation of edge data or a list tuples specifying dictionary
       key names and types for edge data.

    Returns
    -------
    G: EasyGraph Graph
        The graph corresponding to lines

    Examples
    --------
    Edgelist with no data:

    >>> lines = ["1 2", "2 3", "3 4"]
    >>> G = eg.parse_edgelist(lines, nodetype=int)
    >>> list(G)
    [1, 2, 3, 4]
    >>> list(G.edges)
    [(1, 2), (2, 3), (3, 4)]

    Edgelist with data in Python dictionary representation:

    >>> lines = ["1 2 {'weight': 3}", "2 3 {'weight': 27}", "3 4 {'weight': 3.0}"]
    >>> G = eg.parse_edgelist(lines, nodetype=int)
    >>> list(G)
    [1, 2, 3, 4]
    >>> list(G.edges)
    [(1, 2, {'weight': 3}), (2, 3, {'weight': 27}), (3, 4, {'weight': 3.0})]

    Edgelist with data in a list:

    >>> lines = ["1 2 3", "2 3 27", "3 4 3.0"]
    >>> G = eg.parse_edgelist(lines, nodetype=int, data=(("weight", float),))
    >>> list(G)
    [1, 2, 3, 4]
    >>> list(G.edges)
    [(1, 2, {'weight': 3.0}), (2, 3, {'weight': 27.0}), (3, 4, {'weight': 3.0})]

    See Also
    --------
    read_weighted_edgelist
    """
    from ast import literal_eval

    G = eg.empty_graph(0, create_using)
    for line in lines:
        if comments is not None:
            p = line.find(comments)
            if p >= 0:
                line = line[:p]
            if not line:
                continue
        # split line, should have 2 or more
        s = line.strip().split(delimiter)
        if len(s) < 2:
            continue
        u = s.pop(0)
        v = s.pop(0)
        d = s
        if nodetype is not None:
            try:
                u = nodetype(u)
                v = nodetype(v)
            except Exception as err:
                raise TypeError(
                    f"Failed to convert nodes {u},{v} to type {nodetype}."
                ) from err

        if len(d) == 0 or data is False:
            # no data or data type specified
            edgedata = {}
        elif data is True:
            # no edge types specified
            try:  # try to evaluate as dictionary
                if delimiter == ",":
                    edgedata_str = ",".join(d)
                else:
                    edgedata_str = " ".join(d)
                edgedata = dict(literal_eval(edgedata_str.strip()))
            except Exception as err:
                raise TypeError(
                    f"Failed to convert edge data ({d}) to dictionary."
                ) from err
        else:
            # convert edge data to dictionary with specified keys and type
            if len(d) != len(data):
                raise IndexError(
                    f"Edge data {d} and data_keys {data} are not the same length"
                )
            edgedata = {}
            for (edge_key, edge_type), edge_value in zip(data, d):
                try:
                    edge_value = edge_type(edge_value)
                except Exception as err:
                    raise TypeError(
                        f"Failed to convert {edge_key} data {edge_value} "
                        f"to type {edge_type}."
                    ) from err
                edgedata.update({edge_key: edge_value})
        G.add_edge(u, v, **edgedata)
    return G


def generate_edgelist(G, delimiter=" ", data=True):
    """Generate a single line of the graph G in edge list format.

    Parameters
    ----------
    G : EasyGraph graph

    delimiter : string, optional
       Separator for node labels

    data : bool or list of keys
       If False generate no edge data.  If True use a dictionary
       representation of edge data.  If a list of keys use a list of data
       values corresponding to the keys.

    Returns
    -------
    lines : string
        Lines of data in adjlist format.

    Examples
    --------
    >>> G = eg.lollipop_graph(4, 3)
    >>> G[1][2]["weight"] = 3
    >>> G[3][4]["capacity"] = 12
    >>> for line in eg.generate_edgelist(G, data=False):
    ...     print(line)
    0 1
    0 2
    0 3
    1 2
    1 3
    2 3
    3 4
    4 5
    5 6

    >>> for line in eg.generate_edgelist(G):
    ...     print(line)
    0 1 {}
    0 2 {}
    0 3 {}
    1 2 {'weight': 3}
    1 3 {}
    2 3 {}
    3 4 {'capacity': 12}
    4 5 {}
    5 6 {}

    >>> for line in eg.generate_edgelist(G, data=["weight"]):
    ...     print(line)
    0 1
    0 2
    0 3
    1 2 3
    1 3
    2 3
    3 4
    4 5
    5 6

    See Also
    --------
    write_adjlist, read_adjlist
    """
    edges = G.edges
    if edges and len(edges[0]) > 3:
        # multigraph
        edges = ((u, v, d) for u, v, _, d in edges)
    if data is True:
        for u, v, d in edges:
            e = u, v, dict(d)
            yield delimiter.join(map(str, e))
    elif data is False:
        for u, v, _ in edges:
            e = u, v
            yield delimiter.join(map(str, e))
    else:
        for u, v, d in edges:
            e = [u, v]
            try:
                e.extend(d[k] for k in data)
            except KeyError:
                pass  # missing data for this edge, should warn?
            yield delimiter.join(map(str, e))


@open_file(1, mode="wb")
def write_edgelist(G, path, comments="#", delimiter=" ", data=True, encoding="utf-8"):
    """Write graph as a list of edges.

    Parameters
    ----------
    G : graph
       A EasyGraph graph
    path : file or string
       File or filename to write. If a file is provided, it must be
       opened in 'wb' mode. Filenames ending in .gz or .bz2 will be compressed.
    comments : string, optional
       The character used to indicate the start of a comment
    delimiter : string, optional
       The string used to separate values.  The default is whitespace.
    data : bool or list, optional
       If False write no edge data.
       If True write a string representation of the edge data dictionary..
       If a list (or other iterable) is provided, write the  keys specified
       in the list.
    encoding: string, optional
       Specify which encoding to use when writing file.

    Examples
    --------
    >>> G = eg.path_graph(4)
    >>> eg.write_edgelist(G, "test.edgelist")
    >>> G = eg.path_graph(4)
    >>> fh = open("test.edgelist", "wb")
    >>> eg.write_edgelist(G, fh)
    >>> eg.write_edgelist(G, "test.edgelist.gz")
    >>> eg.write_edgelist(G, "test.edgelist.gz", data=False)

    >>> G = eg.Graph()
    >>> G.add_edge(1, 2, weight=7, color="red")
    >>> eg.write_edgelist(G, "test.edgelist", data=False)
    >>> eg.write_edgelist(G, "test.edgelist", data=["color"])
    >>> eg.write_edgelist(G, "test.edgelist", data=["color", "weight"])

    See Also
    --------
    read_edgelist
    write_weighted_edgelist
    """

    for line in generate_edgelist(G, delimiter, data):
        line += "\n"
        path.write(line.encode(encoding))


@open_file(0, mode="rb")
def read_edgelist(
    path,
    comments="#",
    delimiter=None,
    create_using=None,
    nodetype=None,
    data=True,
    edgetype=None,
    encoding="utf-8",
):
    """Read a graph from a list of edges.

    Parameters
    ----------
    path : file or string
       File or filename to read. If a file is provided, it must be
       opened in 'rb' mode.
       Filenames ending in .gz or .bz2 will be uncompressed.
    comments : string, optional
       The character used to indicate the start of a comment. To specify that
       no character should be treated as a comment, use ``comments=None``.
    delimiter : string, optional
       The string used to separate values.  The default is whitespace.
    create_using : EasyGraph graph constructor, optional (default=eg.Graph)
       Graph type to create. If graph instance, then cleared before populated.
    nodetype : int, float, str, Python type, optional
       Convert node data from strings to specified type
    data : bool or list of (label,type) tuples
       Tuples specifying dictionary key names and types for edge data
    edgetype : int, float, str, Python type, optional OBSOLETE
       Convert edge data from strings to specified type and use as 'weight'
    encoding: string, optional
       Specify which encoding to use when reading file.

    Returns
    -------
    G : graph
       A easygraph Graph or other type specified with create_using

    Examples
    --------
    >>> eg.write_edgelist(eg.path_graph(4), "test.edgelist")
    >>> G = eg.read_edgelist("test.edgelist")

    >>> fh = open("test.edgelist", "rb")
    >>> G = eg.read_edgelist(fh)
    >>> fh.close()

    >>> G = eg.read_edgelist("test.edgelist", nodetype=int)
    >>> G = eg.read_edgelist("test.edgelist", create_using=eg.DiGraph)

    Edgelist with data in a list:

    >>> textline = "1 2 3"
    >>> fh = open("test.edgelist", "w")
    >>> d = fh.write(textline)
    >>> fh.close()
    >>> G = eg.read_edgelist("test.edgelist", nodetype=int, data=(("weight", float),))
    >>> list(G)
    [1, 2]
    >>> list(G.edges)
    [(1, 2, {'weight': 3.0})]

    See parse_edgelist() for more examples of formatting.

    See Also
    --------
    parse_edgelist
    write_edgelist

    Notes
    -----
    Since nodes must be hashable, the function nodetype must return hashable
    types (e.g. int, float, str, frozenset - or tuples of those, etc.)
    """
    lines = (line if isinstance(line, str) else line.decode(encoding) for line in path)
    return parse_edgelist(
        lines,
        comments=comments,
        delimiter=delimiter,
        create_using=create_using,
        nodetype=nodetype,
        data=data,
    )


def write_weighted_edgelist(G, path, comments="#", delimiter=" ", encoding="utf-8"):
    """Write graph G as a list of edges with numeric weights.

    Parameters
    ----------
    G : graph
       A EasyGraph graph
    path : file or string
       File or filename to write. If a file is provided, it must be
       opened in 'wb' mode.
       Filenames ending in .gz or .bz2 will be compressed.
    comments : string, optional
       The character used to indicate the start of a comment
    delimiter : string, optional
       The string used to separate values.  The default is whitespace.
    encoding: string, optional
       Specify which encoding to use when writing file.

    Examples
    --------
    >>> G = eg.Graph()
    >>> G.add_edge(1, 2, weight=7)
    >>> eg.write_weighted_edgelist(G, "test.weighted.edgelist")

    See Also
    --------
    read_edgelist
    write_edgelist
    read_weighted_edgelist
    """
    write_edgelist(
        G,
        path,
        comments=comments,
        delimiter=delimiter,
        data=("weight",),
        encoding=encoding,
    )


def read_weighted_edgelist(
    path,
    comments="#",
    delimiter=None,
    create_using=None,
    nodetype=None,
    encoding="utf-8",
):
    """Read a graph as list of edges with numeric weights.

    Parameters
    ----------
    path : file or string
       File or filename to read. If a file is provided, it must be
       opened in 'rb' mode.
       Filenames ending in .gz or .bz2 will be uncompressed.
    comments : string, optional
       The character used to indicate the start of a comment.
    delimiter : string, optional
       The string used to separate values.  The default is whitespace.
    create_using : EasyGraph graph constructor, optional (default=eg.Graph)
       Graph type to create. If graph instance, then cleared before populated.
    nodetype : int, float, str, Python type, optional
       Convert node data from strings to specified type
    encoding: string, optional
       Specify which encoding to use when reading file.

    Returns
    -------
    G : graph
       A easygraph Graph or other type specified with create_using

    Notes
    -----
    Since nodes must be hashable, the function nodetype must return hashable
    types (e.g. int, float, str, frozenset - or tuples of those, etc.)

    Example edgelist file format.

    With numeric edge data::

     # read with
     # >>> G=eg.read_weighted_edgelist(fh)
     # source target data
     a b 1
     a c 3.14159
     d e 42

    See Also
    --------
    write_weighted_edgelist
    """
    return read_edgelist(
        path,
        comments=comments,
        delimiter=delimiter,
        create_using=create_using,
        nodetype=nodetype,
        data=(("weight", float),),
        encoding=encoding,
    )
