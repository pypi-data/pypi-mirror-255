import ast
import os

from modguard.core.boundary import BoundaryTrie
from modguard.errors import ModguardParseError
from modguard.public import public
from .public import get_public_members
from .utils import file_to_module_path, walk_pyfiles


class BoundaryFinder(ast.NodeVisitor):
    def __init__(self):
        self.is_modguard_boundary_imported = False
        self.found_boundary = False

    def visit_ImportFrom(self, node):
        # Check if 'Boundary' is imported specifically from a 'modguard'-rooted module
        if (node.module == "modguard" or node.module.startswith("modguard.")) and any(
            alias.name == "Boundary" for alias in node.names
        ):
            self.is_modguard_boundary_imported = True
        self.generic_visit(node)

    def visit_Import(self, node):
        # Check if 'modguard' is imported
        for alias in node.names:
            if alias.name == "modguard":
                self.is_modguard_boundary_imported = True
        self.generic_visit(node)

    def visit_Call(self, node):
        if self.is_modguard_boundary_imported:
            if isinstance(node.func, ast.Attribute) and node.func.attr == "Boundary":
                if (
                    isinstance(node.func.value, ast.Name)
                    and node.func.value.id == "modguard"
                ):
                    self.found_boundary = True
            elif isinstance(node.func, ast.Name) and node.func.id == "Boundary":
                # This handles the case where 'Boundary' is imported directly: from modguard import Boundary
                # We are currently ignoring the case where this is still the wrong Boundary (if it has been re-assigned)
                self.found_boundary = True
        self.generic_visit(node)


def has_boundary(file_path: str) -> bool:
    with open(file_path, "r") as file:
        file_content = file.read()

    try:
        parsed_ast = ast.parse(file_content)
        boundary_finder = BoundaryFinder()
        boundary_finder.visit(parsed_ast)
        return boundary_finder.found_boundary
    except SyntaxError as e:
        raise ModguardParseError(f"Syntax error in {file_path}: {e}")


@public
def build_boundary_trie(root: str, exclude_paths: list[str] = None) -> BoundaryTrie:
    boundary_trie = BoundaryTrie()
    # Add an 'outer boundary' containing the entire root path
    # This means a project will pass 'check' by default
    boundary_trie.insert(file_to_module_path(root))

    for dirpath, filename in walk_pyfiles(root, exclude_paths=exclude_paths):
        file_path = os.path.join(dirpath, filename)
        if has_boundary(file_path):
            mod_path = file_to_module_path(file_path)
            boundary_trie.insert(mod_path)

    for dirpath, filename in walk_pyfiles(root, exclude_paths=exclude_paths):
        file_path = os.path.join(dirpath, filename)
        mod_path = file_to_module_path(file_path)
        public_members = get_public_members(file_path)
        for public_member in public_members:
            boundary_trie.register_public_member(mod_path, public_member)

    return boundary_trie
