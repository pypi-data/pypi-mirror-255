import pytest
from modguard.check import check, ErrorInfo
from modguard.parsing.utils import file_to_module_path
from modguard.parsing.boundary import has_boundary
from modguard.parsing.imports import get_imports


def test_file_to_mod_path():
    assert file_to_module_path("__init__.py") == ""
    assert file_to_module_path("domain_one/__init__.py") == "domain_one"
    assert file_to_module_path("domain_one/interface.py") == "domain_one.interface"


def test_has_boundary():
    assert has_boundary("example/domain_one/__init__.py")
    assert not has_boundary("example/domain_one/interface.py")


def test_get_imports():
    assert get_imports("example/domain_one/interface.py") == ["modguard.public"]
    assert set(get_imports("example/domain_one/__init__.py")) == {
        "modguard.Boundary",
        "example.domain_one.interface.domain_one_interface",
    }
    assert set(get_imports("example/__init__.py")) == {
        "modguard.Boundary",
        "example.domain_one.interface.domain_one_interface",
        "example.domain_three.api.public_for_domain_two",
        "example.domain_four",
        "example.domain_four.subsystem.private_subsystem_call",
    }


def test_check():
    expected_errors = [
        ErrorInfo(
            import_mod_path="example.domain_one.interface.domain_one_interface",
            location="example/__init__.py",
            boundary_path="example.domain_one",
        ),
        ErrorInfo(
            import_mod_path="example.domain_three.api.public_for_domain_two",
            location="example/__init__.py",
            boundary_path="example.domain_three",
        ),
        ErrorInfo(
            import_mod_path="example.domain_one.interface.domain_one_interface",
            location="example/domain_three/__init__.py",
            boundary_path="example.domain_one",
        ),
        ErrorInfo(
            import_mod_path="example.domain_four.subsystem.private_subsystem_call",
            location="example/__init__.py",
            boundary_path="example.domain_four.subsystem",
        ),
    ]
    check_results = check("example")

    for expected_error in expected_errors:
        assert (
            expected_error in check_results
        ), f"Missing error: {expected_error.message}"
        check_results.remove(expected_error)
    assert len(check_results) == 0, "\n".join(
        (result.message for result in check_results)
    )
