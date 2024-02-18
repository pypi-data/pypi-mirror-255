"""Generic utility functions."""
import os
import urllib.parse
from pathlib import Path
from typing import Dict, Generator, List, Optional, Set, Tuple, Union

from ragraph.graph import Graph
from ragraph.node import Node

from raesl import logger
from raesl.types import Location, Position, Range


def get_esl_paths(*paths: Union[str, Path]) -> List[Path]:
    """Get a sorted list of ESL file paths from multiple file or directory paths."""
    if not paths:
        raise ValueError("No paths were specified.")

    result: Set[Path] = set()

    pathlist = list(paths)
    for path in pathlist:
        logger.debug(f"Resolving '{path}'...")
        if isinstance(path, list):
            pathlist.extend(path)
            continue
        p = Path(path)

        if not p.exists():
            logger.info(f"Skipped '{p}' as it does not exist.")
            continue

        if p.is_dir():
            result.update(
                p for p in p.glob("**/*.esl") if not any(part.startswith(".") for part in p.parts)
            )

        if p.is_file():
            result.add(p)

    if not result:
        raise ValueError("No ESL files found.")

    return sorted(result)


def check_output_path(fpath: Union[str, Path], force: bool) -> Path:
    """Check output filepath versus force overwrite status."""
    p = Path(fpath)

    if p.exists() and not force:
        raise ValueError(f"Path {p} already exists and force overwrite isn't set.")

    if p.is_dir():
        raise ValueError(f"Path {p} is a directory.")

    return p


def get_location(
    uri: str = "Unknown",
    start_line: int = 0,
    start_character: int = 0,
    end_line: Optional[int] = None,
    end_character: Optional[int] = None,
) -> Location:
    """Generation utility to quickly drum up a location.

    Arguments:
        uri: Location uri.
        start_line: Location's range start line.
        start_character: Location's range start offset.
        end_line: Optional Location's range end line (otherwise identical to start.)
        end_character: Optional Location's range end offset (otherwise identical to
            start.)

    Returns:
        Newly created location instance.
    """
    end_line = start_line if end_line is None else end_line
    end_character = start_character if end_character is None else end_character

    return Location(
        uri,
        Range(Position(start_line, start_character), Position(end_line, end_character)),
    )


def cleanup_path(path: Union[str, Path]) -> Path:
    """Cleanup pathname for some typical mistakes."""
    p = str(path)
    result = uri_to_path(p)
    return result


def uri_to_path(uri: str) -> Path:
    """Convert a file URI to a regular path."""
    parsed = urllib.parse.unquote(urllib.parse.urlparse(uri).path)

    if os.name == "nt" and parsed.startswith("/"):
        parsed = parsed[1:]

    return Path(parsed)


def path_to_uri(path: Union[str, Path]) -> str:
    """Convert a path to a file URI."""
    if str(path).startswith("file:"):
        return str(path)
    return Path(path).resolve().as_uri()


def split_first_dot(name: str) -> Tuple[str, str, int]:
    """Split the provided name on the first dot if it exists, return both parts, and
    the length of the dot.
    """
    i = name.find(".")
    if i >= 0:
        return name[:i], name[i + 1 :], 1
    else:
        return name, "", 0


def get_first_namepart(name: str) -> str:
    """Return the name upto and excluding the first dot."""
    i = name.find(".")
    if i < 0:
        return name
    return name[:i]


def get_scoped_nodes(graph: Graph, scopes: Dict[str, Optional[int]]) -> List[Node]:
    """Get scoped nodes, being subtrees of the graph of varying depth.

    Arguments:
        graph: Graph data.
        scopes: Node names mapped to depths of the subtree to include. A depth of
            :obj:`None` includes the whole subtree starting at that node.

    Returns:
        List of nodes in all given scopes.
    """
    seen: Set[str] = set()
    nodes = []

    for name, depth in scopes.items():
        try:
            node = graph[name]
        except KeyError:
            raise KeyError(
                f"Node '{name}' does not exist in the graph. "
                "Make sure you provide the entire instantiated path "
                "(e.g. 'world.component.subcomponent')."
            )

        for candidate in yield_subtree(node, depth):
            if candidate.name in seen:
                continue
            nodes.append(candidate)

    return nodes


def yield_subtree(root: Node, depth: Optional[int]) -> Generator[Node, None, None]:
    """Yield nodes from a given subtree starting at Node and with given depth.

    Arguments:
        root: Root node of subtree.
        depth: Depth of subtree. If None, defaults to full depth.

    Yields:
        Nodes in the subtree.
    """
    yield root

    if depth is None or depth > 0:
        for c in root.children:
            yield from yield_subtree(c, None if depth is None else depth - 1)
