# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/markdown/03_markdown_api.ipynb.

# %% auto 0
__all__ = ['export_markdown_notebook']

# %% ../../nbs/markdown/03_markdown_api.ipynb 5
import io
from typing import Dict, Iterable, Sequence, Tuple

# %% ../../nbs/markdown/03_markdown_api.ipynb 6
from ..api import handle_notebook

from beetroot.markdown.transformations import (
    EscapeEndLineSlashesWithinLatexMath,
    EscapeUnderscoresWithinLatexMath,
    MultiTransformer,
    ReplaceSingleDollarDelimiters,
    Transformer,
    Unindent,
)
from beetroot.markdown.source import (
    MarkdownSourceHandler,
)
from .outputs import MarkdownOutputHandler, MarkdownCompletion

# %% ../../nbs/markdown/03_markdown_api.ipynb 7
def export_markdown_notebook(
    nb_json: Dict,
    markdown_source_transformer=Transformer(),
    python_source_transformer=Transformer(),
    output_transformers_map: Dict[str, Transformer] = {},
) -> Tuple[str, Iterable[MarkdownCompletion]]:
    stream = io.StringIO()
    source_handler = MarkdownSourceHandler(
        stream=stream,
        markdown_source_transformer=markdown_source_transformer,
        python_source_transformer=python_source_transformer,
    )
    output_handler = MarkdownOutputHandler(stream, output_transformers_map)

    completions = handle_notebook(nb_json, source_handler, output_handler)

    stream.seek(0)
    return stream.read(), completions
