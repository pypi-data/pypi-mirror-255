import sys
from ast import *


if sys.version_info < (3, 9):
    import io
    from .ast_unparse import Unparser

    def unparse(tree: AST) -> str:
        with io.StringIO() as output_file:
            Unparser(tree, output_file)
            content = output_file.getvalue()
        return content.strip()
