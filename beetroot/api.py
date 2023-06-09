# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/00_api.ipynb.

# %% auto 0
__all__ = ['SourceHandler', 'OutputHandler', 'handle_notebook']

# %% ../nbs/00_api.ipynb 5
from typing import Dict, Iterable, List, Protocol, Sequence, TypeVar

# %% ../nbs/00_api.ipynb 6
class SourceHandler(Protocol):
    """High-level API for handling cell source"""

    def handle_markdown(self, lines: Sequence[str]):
        """Handle the source lines for a markdown cell

        Parameters
        ----------
        lines
            The lines of source text
        """
        pass

    def handle_python_source(self, lines: Sequence[str]) -> bool:
        """Handle the source lines for a python code cell
        
        Parameters
        ----------
        lines 
            The lines of source text

        Returns
        -------
        bool 
            Indicates whether the output should be handled for \
            this cell.
        """
        return False

# %% ../nbs/00_api.ipynb 9
TOutputResult = TypeVar("TOutputResult", covariant=True)

# %% ../nbs/00_api.ipynb 10
class OutputHandler(Protocol[TOutputResult]):
    """High-level API for handling cell outputs"""

    def handle_output(self, output: Dict) -> TOutputResult:
        """Handle a single cell output
        
        Parameters
        ----------
        output
            a Dict representing a JSON output element as \ 
            defined in the [notebook file format](https://nbformat.readthedocs.io/en/latest/format_description.html#code-cell-outputs)

        Returns
        -------
        TOutputResult
            a result whose type is defined by the implementation \
            (typically a callable that completes any \
            asynchronous processing required)                    
        """
        pass

# %% ../nbs/00_api.ipynb 12
def handle_notebook(
    nb_json: Dict,
    source_handler: SourceHandler,
    output_handler: OutputHandler[TOutputResult],
) -> Iterable[TOutputResult]:
    """
    Handle a notebook with beetroot

    Parameters
    ----------
    nb_json
        A Dict representing the content of a notebook as JSON
    
    source_handler
        A handler for source elements that conforms to the \
        `SourceHandler` protocol

    output_handler
        A handler for output elements that conforms to the \
        `OutputHandler` protocol

    Returns
    -------
    Iterable[TOutputResult]
        An iterable of results returned from the output handler
    """
    results: List[TOutputResult] = []

    for cell in nb_json["cells"]:
        if cell["cell_type"] == "markdown":
            source_handler.handle_markdown(cell["source"])
        elif cell["cell_type"] == "code":
            should_show_output = source_handler.handle_python_source(cell["source"])

            if not should_show_output:
                continue

            for output in cell["outputs"]:
                result = output_handler.handle_output(output)
                results.append(result)

    return results
