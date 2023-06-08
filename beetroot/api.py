# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/02_api.ipynb.

# %% auto 0
__all__ = ['Transformer', 'export_notebook']

# %% ../nbs/02_api.ipynb 5
import io
from typing import Callable, Dict, Iterable, Reversible, Sequence, Tuple

# %% ../nbs/02_api.ipynb 6
from .source import emit_markdown_source, emit_python_source
from beetroot.outputs import (
    Completion,
    emit_display_data_output,
    emit_execute_result_output,
    emit_stream_output,
)

# %% ../nbs/02_api.ipynb 7
class Transformer:
    """Base class for all content transformers."""

    def emit_before(self, stream: io.TextIOBase):
        """Implement this method on sub-classes to emit markdown \
            before the set of lines this transformer processes."""
        return

    def process_lines(self, lines: Sequence[str]) -> Sequence[str]:
        """Implement this method on sub-classes to modify the lines \
            this transformer processes."""
        return lines

    def emit_after(self, stream: io.TextIOBase):
        """Implement this method on sub-classes to emit markdown \
            after the set of lines this transformer processes."""
        return

# %% ../nbs/02_api.ipynb 11
def emit_with_transformations(
    transformers: Reversible[Transformer],
    lines: Sequence[str],
    emit_lines_func: Callable[[Sequence[str], io.TextIOBase], None],
    stream: io.TextIOBase,
):
    # Emit all the before output from the transformers.
    # Do it in reversed order so that the first transformer's
    # before output appears closest to the (transformed) lines
    for transformer in reversed(transformers):
        transformer.emit_before(stream)

    # Pass the source lines through all the transformers
    for transformer in transformers:
        lines = transformer.process_lines(lines)

    # Emit the now transformed lines
    emit_lines_func(lines, stream)

    # Emit the after output from the transformers
    for transformer in transformers:
        transformer.emit_after(stream)

# %% ../nbs/02_api.ipynb 13
def export_notebook(
    nb_json: Dict, transformers_map: Dict[str, Reversible[Transformer]] = {}
) -> Tuple[str, Iterable[Completion]]:
    stream = io.StringIO()
    completions = []
    for cell in nb_json["cells"]:
        if cell["cell_type"] == "markdown":
            emit_with_transformations(
                transformers_map.get("markdown/source", []),
                cell["source"],
                emit_markdown_source,
                stream,
            )
            stream.write("\n")
        elif cell["cell_type"] == "code":
            should_show_output = emit_python_source(cell["source"], stream)
            stream.write("\n")

            if not should_show_output:
                continue

            for output in cell["outputs"]:
                output_type = output["output_type"]
                if output_type == "stream":
                    emit_stream_output(output, stream)
                elif output_type == "display_data":
                    completion = emit_display_data_output(output, stream)
                    if completion:
                        completions.append(completion)
                elif output_type == "execute_result":
                    completion = emit_execute_result_output(output, stream)
                    if completion:
                        completions.append(completion)
                stream.write("\n")

    stream.seek(0)
    return stream.read(), completions
