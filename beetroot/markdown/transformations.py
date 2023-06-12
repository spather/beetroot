# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/markdown/00_transformations.ipynb.

# %% auto 0
__all__ = ['Transformer', 'MultiTransformer', 'emit_with_transformation', 'ReplaceSingleDollarDelimiters',
           'EscapeUnderscoresWithinLatexMath', 'EscapeEndLineSlashesWithinLatexMath', 'Unindent']

# %% ../../nbs/markdown/00_transformations.ipynb 5
import io
import re
from typing import Callable, Iterable, Sequence

# %% ../../nbs/markdown/00_transformations.ipynb 6
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

# %% ../../nbs/markdown/00_transformations.ipynb 10
class MultiTransformer(Transformer):
    def __init__(self, transformers: Iterable[Transformer]):
        # Store the passed in transformers as a list
        # so that we can later call reverse() on it.
        self.transformers = list(transformers)

    def emit_before(self, stream: io.TextIOBase):
        # Emit all the before output from the transformers.
        # Do it in reversed order so that the first transformer's
        # before output appears closest to the (transformed) lines
        for transformer in reversed(self.transformers):
            transformer.emit_before(stream)

    def process_lines(self, lines: Sequence[str]) -> Sequence[str]:
        # Pass the source lines through all the transformers
        for transformer in self.transformers:
            lines = transformer.process_lines(lines)
        return lines

    def emit_after(self, stream: io.TextIOBase):
        # Emit the after output from the transformers
        for transformer in self.transformers:
            transformer.emit_after(stream)

# %% ../../nbs/markdown/00_transformations.ipynb 11
def emit_with_transformation(
    transformer: Transformer,
    lines: Sequence[str],
    emit_lines_func: Callable[[Sequence[str], io.TextIOBase], None],
    stream: io.TextIOBase,
):
    transformer.emit_before(stream)

    emit_lines_func(transformer.process_lines(lines), stream)

    transformer.emit_after(stream)

# %% ../../nbs/markdown/00_transformations.ipynb 13
class ReplaceSingleDollarDelimiters(Transformer):
    """Transformer that replaces $ delimiters in inline latex\
        with \\\\( and \\\\)."""

    def process_lines(self, lines: Sequence[str]) -> Sequence[str]:
        regex = r"(?<!\$)\$(?!\$)(.*?[^\\])\$(?!\$)(?!\w)"
        replacement = r"\\\\(\1\\\\)"

        return [re.sub(regex, replacement, line) for line in lines]

# %% ../../nbs/markdown/00_transformations.ipynb 15
class EscapeUnderscoresWithinLatexMath(Transformer):
    """Transformer that replaces underscores within latex\
        math expressions with \_."""

    def process_lines(self, lines: Sequence[str]) -> Sequence[str]:
        regex_inline = r"(?<!\$)\$(?!\$)(.*?[^\\])\$(?!\$)"
        regex_block = r"\$\$([\s\S]*?)\$\$"

        # We want to handle cases where math expressions could be in a single
        # line or spread across multiple lines. So we'll join the lines with
        # a dummy token separator into a single string, perform the substitutions
        # and the split back into lines on the dummy token.
        dummy_token = "DUMMY+TOKEN+DO+NOT+USE"
        text = dummy_token.join(lines)

        # Escaping underscores in block math expressions
        text = re.sub(
            regex_block, lambda match: re.sub(r"_", r"\_", match.group()), text
        )

        # Escaping underscores in inline math expressions
        text = re.sub(
            regex_inline, lambda match: re.sub(r"_", r"\_", match.group()), text
        )

        processed_lines = text.split(dummy_token)
        return processed_lines

# %% ../../nbs/markdown/00_transformations.ipynb 17
class EscapeEndLineSlashesWithinLatexMath(Transformer):
    """Transformer that replaces slashes ("\\") at the end of lines\
        within math block expressions expressions with "\\\\".\
        Handles the case where the "\\" is followed by a line width\
        e.g. "\\[2em]"."""

    def process_lines(self, lines: Sequence[str]) -> Sequence[str]:
        regex_block = r"\$\$([\s\S]*?)\$\$"

        # We want to handle cases where math expressions could be in a single
        # line or spread across multiple lines. So we'll join the lines with
        # a dummy token separator into a single string, perform the substitutions
        # and the split back into lines on the dummy token.
        dummy_token = "DUMMY+TOKEN+DO+NOT+USE"
        text = dummy_token.join(lines)

        text = re.sub(
            regex_block,
            lambda match: re.sub(
                r"\\\\(?=\[.*?\]$|$)", r"\\\\\\\\", match.group(), flags=re.MULTILINE
            ),
            text,
        )

        processed_lines = text.split(dummy_token)
        return processed_lines

# %% ../../nbs/markdown/00_transformations.ipynb 19
class Unindent(Transformer):
    """Transformer that removes leading indentation from a set\
        of lines. Will determine how far indented the first line \
        is and then remove \
        min(indentation of first non-empty line, indentation of current line) \
        for each subsequent line."""

    def process_lines(self, lines: Sequence[str]) -> Sequence[str]:
        i = 0
        for i, line in enumerate(lines):
            if line.strip() != "":
                break

        # i is now the index of the first line that is not all whitespace
        # or len(lines)-1 if all the lines were just whitespace.

        if i == len(lines) - 1 and line.strip() == "":
            # Everything was whitespace, just return it
            # unmodified
            return lines

        # If we're here, i is the index of the first line that is not
        # all whitespace.

        first_line_indent = len(lines[i]) - len(lines[i].lstrip())

        processed_lines = []
        for line in lines[i:]:
            cur_indent = len(line) - len(line.lstrip())
            remove_count = min(first_line_indent, cur_indent)
            processed_lines.append(line[remove_count:])

        return processed_lines
