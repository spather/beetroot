# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/00_transformations.ipynb.

# %% auto 0
__all__ = ['Transformer', 'emit_with_transformations']

# %% ../nbs/00_transformations.ipynb 4
import io
from typing import Callable, Reversible, Sequence

# %% ../nbs/00_transformations.ipynb 5
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

# %% ../nbs/00_transformations.ipynb 9
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
