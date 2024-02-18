import ast
from typing import Optional

from modguard import public
from modguard.core.public import PublicMember
from modguard.errors import ModguardParseError

from .utils import file_to_module_path


class ModguardImportVisitor(ast.NodeVisitor):
    def __init__(self, module_name: str):
        self.module_name = module_name
        self.import_found = False

    def visit_ImportFrom(self, node):
        if (node.module == "modguard" or node.module.startswith("modguard.")) and any(
            alias.name == self.module_name for alias in node.names
        ):
            self.import_found = True
            return
        self.generic_visit(node)

    def visit_Import(self, node):
        for alias in node.names:
            if alias.name == "modguard":
                self.import_found = True
                return
        self.generic_visit(node)


class PublicMemberVisitor(ast.NodeVisitor):
    def __init__(self, current_mod_path: str, is_package: bool = False):
        self.is_modguard_public_imported = False
        self.current_mod_path = current_mod_path
        self.is_package = is_package
        self.public_members: list[PublicMember] = []

    def visit_ImportFrom(self, node):
        if (node.module == "modguard" or node.module.startswith("modguard.")) and any(
            alias.name == "public" for alias in node.names
        ):
            self.is_modguard_public_imported = True
        self.generic_visit(node)

    def visit_Import(self, node):
        for alias in node.names:
            if alias.name == "modguard":
                self.is_modguard_public_imported = True
        self.generic_visit(node)

    def _extract_allowlist(self, public_call: ast.Call) -> Optional[list[str]]:
        for kw in public_call.keywords:
            if kw.arg == "allowlist":
                allowlist_value = kw.value
                if isinstance(allowlist_value, ast.List):
                    return [
                        elt.value
                        for elt in allowlist_value.elts
                        if isinstance(elt, ast.Constant) and isinstance(elt.value, str)
                    ] or None
        return None

    def _add_public_member_from_decorator(self, node: ast.AST, decorator: ast.expr):
        if (
            isinstance(decorator, ast.Call)
            and isinstance(decorator.func, ast.Name)
            and decorator.func.id == "public"
        ):
            # This means @public is called with arguments
            self.public_members.append(
                PublicMember(
                    name=node.name, allowlist=self._extract_allowlist(decorator)
                )
            )
        elif isinstance(decorator, ast.Name) and decorator.id == "public":
            self.public_members.append(PublicMember(name=node.name))
        elif isinstance(decorator, ast.Attribute) and decorator.attr == "public":
            value = decorator.value
            if isinstance(value, ast.Name) and value.id == "modguard":
                self.public_members.append(PublicMember(name=node.name))

    def visit_FunctionDef(self, node):
        if self.is_modguard_public_imported:
            for decorator in node.decorator_list:
                self._add_public_member_from_decorator(node=node, decorator=decorator)
        self.generic_visit(node)

    def visit_ClassDef(self, node):
        if self.is_modguard_public_imported:
            for decorator in node.decorator_list:
                self._add_public_member_from_decorator(node=node, decorator=decorator)
        self.generic_visit(node)

    def visit_Call(self, node):
        parent_node = node.parent
        top_level = isinstance(parent_node, ast.Module)
        top_level_expr = isinstance(parent_node, ast.Expr) and isinstance(
            parent_node.parent, ast.Module
        )
        if (
            self.is_modguard_public_imported
            and (top_level or top_level_expr)
            and isinstance(node.func, ast.Name)
            and node.func.id == "public"
        ):
            # public() has been called at the top-level,
            # so we add it as the sole PublicMember and return
            self.public_members = [
                PublicMember(
                    name="",
                    allowlist=self._extract_allowlist(node),
                )
            ]
            return
        self.generic_visit(node)

    def visit(self, node):
        # Inject a 'parent' attribute to each node for easier parent tracking
        for child in ast.iter_child_nodes(node):
            child.parent = node
        super().visit(node)


def get_public_members(file_path: str) -> list[PublicMember]:
    with open(file_path, "r") as file:
        file_content = file.read()

    try:
        parsed_ast = ast.parse(file_content)
    except SyntaxError as e:
        raise ModguardParseError(f"Syntax error in {file_path}: {e}")

    mod_path = file_to_module_path(file_path)
    public_member_visitor = PublicMemberVisitor(
        is_package=file_path.endswith("__init__.py"), current_mod_path=mod_path
    )
    public_member_visitor.visit(parsed_ast)
    return public_member_visitor.public_members


class MemberFinder(ast.NodeVisitor):
    def __init__(self, member_name: str):
        self.member_name = member_name
        self.matched_lineno: Optional[int] = None
        self.depth = 0

    def visit_FunctionDef(self, node):
        if self.depth == 0 and node.name == self.member_name:
            self.matched_lineno = node.lineno
            return

        self.depth += 1
        self.generic_visit(node)
        self.depth -= 1

    def visit_ClassDef(self, node):
        if self.depth == 0 and node.name == self.member_name:
            self.matched_lineno = node.lineno
            return

        self.depth += 1
        self.generic_visit(node)
        self.depth -= 1


def _public_module_prelude(should_import: bool = True) -> str:
    if should_import:
        return "import modguard\nmodguard.public()\n"
    return "modguard.public()\n"


IMPORT_MODGUARD = "import modguard"
PUBLIC_DECORATOR = "@modguard.public"


@public
def mark_as_public(file_path: str, member_name: str = ""):
    with open(file_path, "r") as file:
        file_content = file.read()

    try:
        parsed_ast = ast.parse(file_content)
    except SyntaxError as e:
        raise ModguardParseError(f"Syntax error in {file_path}: {e}")

    modguard_import_visitor = ModguardImportVisitor("public")
    modguard_import_visitor.visit(parsed_ast)
    modguard_public_is_imported = modguard_import_visitor.import_found

    if not member_name:
        with open(file_path, "w") as file:
            file.write(
                _public_module_prelude(should_import=not modguard_public_is_imported)
                + file_content
            )
        return

    member_finder = MemberFinder(member_name)
    member_finder.visit(parsed_ast)
    if member_finder.matched_lineno is None:
        raise ModguardParseError(
            f"Failed to find member {member_name} in file {file_path}"
        )

    with open(file_path, "w") as file:
        file_lines = file_content.splitlines(keepends=True)
        lines_to_write = [
            *file_lines[: member_finder.matched_lineno - 1],
            PUBLIC_DECORATOR + "\n",
            *file_lines[member_finder.matched_lineno - 1 :],
        ]
        if not modguard_public_is_imported:
            lines_to_write = [IMPORT_MODGUARD + "\n", *lines_to_write]

        file.write("".join(lines_to_write))
