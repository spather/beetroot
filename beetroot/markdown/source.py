# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/markdown/01_source.ipynb.

# %% auto 0
__all__ = ['MarkdownSourceHandler']

# %% ../../nbs/markdown/01_source.ipynb 5
import io
from typing import Dict, Iterable, Optional, Sequence, Tuple, Union

# %% ../../nbs/markdown/01_source.ipynb 6
from ..api import SourceHandler
from beetroot.markdown.transformations import (
    emit_with_transformation,
    Transformer,
    TransformerWithDirectives,
)

# %% ../../nbs/markdown/01_source.ipynb 7
def emit_markdown_source(markdown: Iterable[str], stream: io.TextIOBase):
    for line in markdown:
        stream.write(line)
    stream.write("\n")

# %% ../../nbs/markdown/01_source.ipynb 8
def is_directive_line(line: str):
    return line.startswith("#|") or line.startswith("# |")


def parse_directive_line(line: str) -> Tuple[str, Optional[Union[bool, str]]]:
    assert is_directive_line(line)

    directive = line.lstrip("# |").strip()

    # A directive is either a single key or key: value
    key = directive
    value_str: Optional[str] = None

    colon_index = directive.find(":")
    if colon_index != -1:
        key = directive[:colon_index].strip()
        value_str = directive[colon_index + 1 :].strip()

    # There was no value; treat it as None
    if value_str is None:
        return key, None

    # Deal with string forms of true and false
    # These directives are technically YAML, so allowing all the values
    # for bool per [the spec](https://yaml.org/type/bool.html).

    true_vals = [
        "y",
        "Y",
        "yes",
        "Yes",
        "YES",
        "true",
        "True",
        "TRUE",
        "on",
        "On",
        "ON",
    ]
    false_vals = [
        "n",
        "N",
        "no",
        "No",
        "NO",
        "false",
        "False",
        "FALSE",
        "off",
        "Off",
        "OFF",
    ]

    value: Optional[bool] = None
    if value_str in true_vals:
        value = True
    elif value_str in false_vals:
        value = False

    if value is not None:
        return key, value

    # We couldn't parse a bool value, just return the key and the string
    return key, value_str

# %% ../../nbs/markdown/01_source.ipynb 10
def parse_and_extract_directives_from_python_source(
    source: Sequence[str],
) -> Tuple[Sequence[str], Dict[str, Optional[Union[bool, str]]]]:
    directives = {}
    i = 0  # initialize explicitly because `source` may be empty
    for i, line in enumerate(source):
        if is_directive_line(line):
            key, value = parse_directive_line(line)
            directives[key] = value
        else:
            # Break out on hitting the first non-directive line
            break

    # Consume any blank lines after the directives:
    j = 0  # initialize explicitly because `source[i:]` may be empty
    for j, line in enumerate(source[i:]):
        if len(line.strip()) > 0:
            break

    return source[i + j :], directives

# %% ../../nbs/markdown/01_source.ipynb 12
def handle_python_source(source: Sequence[str], stream: io.TextIOBase):
    stream.write("```python\n")
    for line in source:
        stream.write(line)
    stream.write("\n```\n")

# %% ../../nbs/markdown/01_source.ipynb 13
class MarkdownSourceHandler(SourceHandler):
    """High-level API for handling cell source"""

    def __init__(
        self,
        stream: io.TextIOBase,
        markdown_source_transformer: Transformer = Transformer(),
        python_source_transformer: TransformerWithDirectives = TransformerWithDirectives(),
    ):
        self.stream = stream
        self.markdown_source_transformer = markdown_source_transformer
        self.python_source_transformer = python_source_transformer

    def handle_markdown(self, lines: Sequence[str]):
        emit_with_transformation(
            self.markdown_source_transformer,
            lines,
            emit_markdown_source,
            self.stream,
        )
        self.stream.write("\n")

    def handle_python_source(self, lines: Sequence[str]) -> bool:
        python_source, directives = parse_and_extract_directives_from_python_source(
            lines
        )

        # Handle directives per https://quarto.org/docs/reference/cells/cells-jupyter.html#code-output
        # and https://quarto.org/docs/reference/cells/cells-jupyter.html#cell-output.
        should_echo = "echo" not in directives or directives["echo"] == True
        should_show_output = "output" not in directives or directives["output"] == True

        if should_echo:
            with self.python_source_transformer.begin_using_directives(directives):
                emit_with_transformation(
                    self.python_source_transformer,
                    python_source,
                    handle_python_source,
                    self.stream,
                )
                self.stream.write("\n")

        return should_show_output
