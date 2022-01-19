#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
an object-oriented version of the notebook toolbox
"""

# Python Standard Library
import base64
import io
import json
import pprint
from pathlib import Path
import notebook_v0 as toolbox         #had to add this to import all the importations

# Third-Party Libraries
import numpy as np
import PIL.Image  # pillow

class Cell:         #defined so that CodeCells and MarkdownCells are well identified
    def __init__(self, ipynb):
        self.id = ipynb["id"]
        self.source = ipynb["source"]

class CodeCell(Cell):
    r"""A Cell of Python code in a Jupyter notebook.

    Args:
        ipynb (dict): a dictionary representing the cell in a Jupyter Notebook.

    Attributes:
        id (int): the cell's id.
        source (list): the cell's source code, as a list of str.
        execution_count (int): number of times the cell has been executed.

    Usage:

        >>> code_cell = CodeCell({
        ...     "cell_type": "code",
        ...     "execution_count": 1,
        ...     "id": "b777420a",
        ...     'source': ['print("Hello world!")']
        ... })
        >>> code_cell.id
        'b777420a'
        >>> code_cell.execution_count
        1
        >>> code_cell.source
        ['print("Hello world!")']
    """

    def __init__(self, ipynb):
        self.id = ipynb["id"]
        self.cell_type = ipynb["cell_type"]
        self.execution_count = ipynb["execution_count"]
        self.source = ipynb["source"]

class MarkdownCell(Cell):
    r"""A Cell of Markdown markup in a Jupyter notebook.

    Args:
        ipynb (dict): a dictionary representing the cell in a Jupyter Notebook.

    Attributes:
        id (int): the cell's id.
        source (list): the cell's source code, as a list of str.

    Usage:

        >>> markdown_cell = MarkdownCell({
        ...    "cell_type": "markdown",
        ...    "id": "a9541506",
        ...    "source": [
        ...        "Hello world!\n",
        ...        "============\n",
        ...        "Print `Hello world!`:"
        ...    ]
        ... })
        >>> markdown_cell.id
        'a9541506'
        >>> markdown_cell.source
        ['Hello world!\n', '============\n', 'Print `Hello world!`:']
    """

    def __init__(self, ipynb):
        self.cell_type = ipynb["cell_type"]
        self.id = ipynb["id"]
        self.source = ipynb["source"]

class Notebook:
    r"""A Jupyter Notebook.

    Args:
        ipynb (dict): a dictionary representing a Jupyter Notebook.

    Attributes:
        version (str): the version of the notebook format.
        cells (list): a list of cells (either CodeCell or MarkdownCell).

    Usage:

        - checking the verion number:

            >>> ipynb = toolbox.load_ipynb("samples/minimal.ipynb")
            >>> nb = Notebook(ipynb)
            >>> nb.version
            '4.5'

        - checking the type of the notebook parts:

            >>> ipynb = toolbox.load_ipynb("samples/hello-world.ipynb")
            >>> nb = Notebook(ipynb)
            >>> isinstance(nb.cells, list)
            True
            >>> isinstance(nb.cells[0], Cell)
            True
    """

    def __init__(self, ipynb):
        self.version = toolbox.get_format_version(ipynb)
        
        cells = []
        for i in toolbox.get_cells(ipynb):
            if i["cell_type"] == "code":
                cells.append(CodeCell(i)) 
            elif i["cell_type"] == "markdown":
                cells.append(MarkdownCell(i))
        self.cells = cells
        

    
    @staticmethod

    def from_file(filename):
        r"""Loads a notebook from an .ipynb file.

        Usage:

            >>> nb = Notebook.from_file("samples/minimal.ipynb")
            >>> nb.version
            '4.5'
        """
        return Notebook(toolbox.load_ipynb(filename))

    def __iter__(self):
        r"""Iterate the cells of the notebook.

        Usage:

            >>> nb = Notebook.from_file("samples/hello-world.ipynb")
            >>> for cell in nb:
            ...     print(cell.id)
            a9541506
            b777420a
            a23ab5ac
        """
        return iter(self.cells)


class PyPercentSerializer:
    r"""Prints a given Notebook in py-percent format.

    Args:
        notebook (Notebook): the notebook to print.

    Usage:
            >>> nb = Notebook.from_file("samples/hello-world.ipynb")
            >>> ppp = PyPercentSerializer(nb)
            >>> print(ppp.to_py_percent()) # doctest: +NORMALIZE_WHITESPACE
            # %% [markdown]
            # Hello world!
            # ============
            # Print `Hello world!`:
            <BLANKLINE>
            # %%
            print("Hello world!")
            <BLANKLINE>
            # %% [markdown]
            # Goodbye! 👋
    """
    def __init__(self, notebook):
        self.notebook = notebook

    def to_py_percent(self):
        r"""Converts the notebook to a string in py-percent format.
        """
        nb = Serializer(self.notebook)
        myJSON = nb.serialize()
        
        raw = toolbox.to_percent(myJSON)
        lst = raw.split("\n")
        lst.insert(4,"")
        lst.insert(7,"")
        res = "\n".join(lst)
        return res
        


    def to_file(self, filename):
        r"""Serializes the notebook to a file

        Args:
            filename (str): the name of the file to write to.

        Usage:

                >>> nb = Notebook.from_file("samples/hello-world.ipynb")
                >>> s = PyPercentSerializer(nb)
                >>> s.to_file("samples/hello-world-serialized-py-percent.py")
        """
        nb = PyPercentSerializer.to_py_percent(self)
        f = open(filename, "w", encoding = "utf-8")
        json.dump(nb, f)
        f.close()



class Serializer:
    r"""Serializes a Jupyter Notebook to a file.

    Args:
        notebook (Notebook): the notebook to print.

    Usage:

        >>> nb = Notebook.from_file("samples/hello-world.ipynb")
        >>> s = Serializer(nb)
        >>> pprint.pprint(s.serialize())  # doctest: +NORMALIZE_WHITESPACE
            {'cells': [{'cell_type': 'markdown',
                'id': 'a9541506',
                'metadata': {},
                'source': ['Hello world!\n',
                           '============\n',
                           'Print `Hello world!`:']},
               {'cell_type': 'code',
                'execution_count': 1,
                'id': 'b777420a',
                'metadata': {},
                'outputs': [],
                'source': ['print("Hello world!")']},
               {'cell_type': 'markdown',
                'id': 'a23ab5ac',
                'metadata': {},
                'source': ['Goodbye! 👋']}],
            'metadata': {},
            'nbformat': 4,
            'nbformat_minor': 5}
        >>> s.to_file("samples/hello-world-serialized.ipynb")
    """

    def __init__(self, notebook):
        self.notebook = notebook

    def serialize(self):
        r"""Serializes the notebook to a JSON object

        Returns:
            dict: a dictionary representing the notebook.
        """
        nb = self.notebook
        cells = []
        for cell in nb.cells:
            if isinstance(cell, CodeCell):
                raw = {"cell_type": cell.cell_type, "execution_count": cell.execution_count, 
                        "id": cell.id, "metadata": {}, "outputs": [], "source": cell.source}
                cells.append(raw)
            elif isinstance(cell, MarkdownCell):
                raw = {"cell_type": cell.cell_type, "id": cell.id, "metadata": {}, "source": cell.source}
                cells.append(raw)
        
        my_JSON = {"cells": cells, "metadata": {}, "nbformat": int(nb.version[0]), "nbformat_minor": int(nb.version[-1])}
        return my_JSON


    def to_file(self, filename):
        r"""Serializes the notebook to a file

        Args:
            filename (str): the name of the file to write to.

        Usage:

                >>> nb = Notebook.from_file("samples/hello-world.ipynb")
                >>> s = Serializer(nb)
                >>> s.to_file("samples/hello-world-serialized.ipynb")
                >>> nb = Notebook.from_file("samples/hello-world-serialized.ipynb")
                >>> for cell in nb:
                ...     print(cell.id)
                a9541506
                b777420a
                a23ab5ac
        """
        my_JSON = Serializer.serialize(self)
        toolbox.save_ipynb(my_JSON, filename)

# +
class Outliner:
    r"""Quickly outlines the strucure of the notebook in a readable format.

    Args:
        notebook (Notebook): the notebook to outline.

    Usage:

            >>> nb = Notebook.from_file("samples/hello-world.ipynb")
            >>> o = Outliner(nb)
            >>> print(o.outline()) # doctest: +NORMALIZE_WHITESPACE
                Jupyter Notebook v4.5
                └─▶ Markdown cell #a9541506
                    ┌  Hello world!
                    │  ============
                    └  Print `Hello world!`:
                └─▶ Code cell #b777420a (1)
                    | print("Hello world!")
                └─▶ Markdown cell #a23ab5ac
                    | Goodbye! 👋
    """
    def __init__(self, notebook):
        self.notebook = notebook

    def outline(self):
        r"""Outlines the notebook in a readable format.

        Returns:
            str: a string representing the outline of the notebook.
        """
        res = f"Jupyter Notebook v{(self.notebook).version}"

        for cell in (self.notebook).cells:
            if isinstance(cell, CodeCell):
                res += f"\n└─▶ Code cell #{cell.id} (1)"
                if len(cell.source) == 1:
                    res += "\n    | " + cell.source[0]
                else:
                    for idx, content in enumerate(cell.source):
                        if idx == 0:
                            res += "\n    ┌  " + content
                        elif idx == len(cell.source) - 1:
                            res += "\n    └  " + content
                        else:
                            res += "\n    |  " + content
            elif isinstance(cell, MarkdownCell):
                res += f"\n└─▶ Markdown cell #{cell.id}"
                if len(cell.source) == 1:
                    res += "\n    | " + cell.source[0]
                else:
                    for idx, content in enumerate(cell.source):
                        if idx == 0:
                            res += "\n    ┌  " + content
                        elif idx == len(cell.source) - 1:
                            res += "    └  " + content
                        else:
                            res += "    |  " + content
        return res