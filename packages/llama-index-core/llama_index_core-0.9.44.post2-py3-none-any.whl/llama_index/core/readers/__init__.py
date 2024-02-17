"""Data Connectors for LlamaIndex.

This module contains the data connectors for LlamaIndex. Each connector inherits
from a `BaseReader` class, connects to a data source, and loads Document objects
from that data source.

You may also choose to construct Document objects manually, for instance
in our `Insert How-To Guide <../how_to/insert.html>`_. See below for the API
definition of a Document - the bare minimum is a `text` property.

"""

from llama_index.core.readers.base import ReaderConfig

# readers
from llama_index.core.readers.file.base import SimpleDirectoryReader
from llama_index.core.readers.file.docs_reader import PDFReader
from llama_index.core.readers.file.html_reader import HTMLTagReader
from llama_index.core.readers.string_iterable import StringIterableReader
from llama_index.core.schema import Document

__all__ = [
    "SimpleDirectoryReader",
    "ReaderConfig",
    "PDFReader",
    "HTMLTagReader",
    "Document",
    "StringIterableReader",
]
