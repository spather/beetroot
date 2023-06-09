# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/02_outputs.ipynb.

# %% auto 0
__all__ = ['Completion', 'OutputHandler']

# %% ../nbs/02_outputs.ipynb 4
import base64
import io
from pathlib import Path
from textwrap import dedent
from typing import Callable, Dict, Iterable, List, Reversible
import uuid

# %% ../nbs/02_outputs.ipynb 5
from .transformations import emit_with_transformations, Transformer

# %% ../nbs/02_outputs.ipynb 6
Completion = Callable[[Path], None]

# %% ../nbs/02_outputs.ipynb 7
def emit_lines(lines: Iterable[str], stream: io.TextIOBase):
    for line in lines:
        stream.write(line)
    if line[-1] != "\n":
        stream.write("\n")


def emit_plaintext(lines: Iterable[str], stream: io.TextIOBase):
    stream.write("```\n")
    emit_lines(lines, stream)
    stream.write("```\n")


def emit_image_data(
    img_data_b64: str,
    stream: io.TextIOBase,
    filename_generator: Callable[[], str] = lambda: str(uuid.uuid4()),
) -> Iterable[Completion]:
    bytes = base64.b64decode(img_data_b64)
    filename = f"{filename_generator()}.png"
    images_dir = "images/"

    def completion(output_dir: Path):
        nonlocal bytes, filename, images_dir

        (output_dir / images_dir).mkdir(exist_ok=True)

        with open(output_dir / images_dir / filename, "wb") as file:
            file.write(bytes)

    stream.write(f"![]({Path(images_dir)/filename})")
    return [completion]


def emit_output_data(
    data: Dict,
    stream: io.TextIOBase,
    transformers_map: Dict[str, Reversible[Transformer]] = {},
) -> Iterable[Completion]:
    lines_mimetypes = ["text/markdown", "text/latex", "text/html"]

    completions: Iterable[Completion] = []
    for mimetype in lines_mimetypes:
        if mimetype in data:
            emit_with_transformations(
                transformers_map.get(f"{mimetype}/data/output", []),
                data[mimetype],
                emit_lines,
                stream,
            )

            return completions

    if "image/png" in data:
        return emit_image_data(data["image/png"], stream)

    if "text/plain" in data:
        emit_with_transformations(
            transformers_map.get("text/plain/data/output", []),
            data["text/plain"],
            emit_plaintext,
            stream,
        )

        return completions

    return completions

# %% ../nbs/02_outputs.ipynb 8
class OutputHandler:
    def __init__(
        self,
        stream: io.TextIOBase,
        transformers_map: Dict[str, Reversible[Transformer]] = {},
    ):
        self.stream = stream
        self.transformers_map = transformers_map

    def handle_output(self, output: Dict) -> Iterable[Completion]:
        completions: List[Completion] = []
        output_type = output["output_type"]
        if output_type == "stream":
            # Handle [stream output](https://nbformat.readthedocs.io/en/latest/format_description.html#stream-output).
            emit_with_transformations(
                self.transformers_map.get("stream/output", []),
                output["text"],
                emit_plaintext,
                self.stream,
            )
        elif output_type == "execute_result":
            # Handle [`execute_result`](https://nbformat.readthedocs.io/en/latest/format_description.html#execute-result) outputs.
            completions.extend(
                emit_output_data(output["data"], self.stream, self.transformers_map)
            )
        elif output_type == "display_data":
            # Handle [`display_data`](https://nbformat.readthedocs.io/en/latest/format_description.html#display-data) outputs.
            completions.extend(
                emit_output_data(output["data"], self.stream, self.transformers_map)
            )

        return completions
